"""Post article to note.com using Selenium (adapted from money-chaos-japan)."""

import sys
import io
import os
import time
import json
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Credentials
NOTE_EMAIL = os.environ.get("NOTE_EMAIL", "alwayswabisabi@gmail.com")
NOTE_PASSWORD = os.environ.get("NOTE_PASSWORD", "PlanB1513t")

ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "..", "media", "content_drafts", "note_final.md")
TAGS = ["ブランド", "リセール", "エルメス", "シャネル", "投資", "お得"]


def _markdown_to_note_body(md_text: str) -> list[dict]:
    """Convert markdown to note.com body format."""
    lines = md_text.strip().split("\n")
    body = []

    for line in lines:
        line = line.rstrip()
        if not line:
            body.append({"type": "p", "text": ""})
        elif line.startswith("## "):
            body.append({"type": "h3", "text": line[3:]})
        elif line.startswith("# "):
            continue  # Skip title (handled separately)
        elif line.startswith("---"):
            body.append({"type": "hr"})
        elif line.startswith("「") or line.startswith("『"):
            body.append({"type": "p", "text": line})
        else:
            body.append({"type": "p", "text": line})

    return body


def create_driver():
    """Create Chrome WebDriver with anti-detection."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1280,900")
    options.add_argument("--lang=ja-JP")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def login_note(driver):
    """Login to note.com."""
    print("Logging in to note.com...")
    driver.get("https://note.com/login")
    time.sleep(3)

    # Email login
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"], input[name="login"]'))
        )
        email_input.clear()
        email_input.send_keys(NOTE_EMAIL)

        pw_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        pw_input.clear()
        pw_input.send_keys(NOTE_PASSWORD)

        # Click login button
        login_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_btn.click()
        time.sleep(5)

        print(f"Logged in. Current URL: {driver.current_url}")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False


def post_article(driver, title: str, body_text: str, tags: list[str]):
    """Post article via note.com editor."""
    print("Navigating to editor...")
    driver.get("https://note.com/notes/new")
    time.sleep(5)

    # Click "テキスト" if prompted
    try:
        text_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "テキスト")]'))
        )
        text_btn.click()
        time.sleep(2)
    except Exception:
        pass

    # Enter title
    try:
        title_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder*="タイトル"], [contenteditable][data-placeholder*="タイトル"], .o-noteContentEditor__title textarea'))
        )
        escaped_title = title.replace('`', "'")
        script = f"""
            var el = arguments[0];
            el.focus();
            document.execCommand('selectAll');
            document.execCommand('insertText', false, `{escaped_title}`);
        """
        driver.execute_script(script, title_el)
        print(f"Title set: {title[:50]}...")
        time.sleep(1)
    except Exception as e:
        print(f"Could not set title: {e}")
        # Try alternative
        try:
            title_el = driver.find_element(By.CSS_SELECTOR, "[contenteditable]")
            title_el.click()
            escaped_t = title.replace('`', "'")
            driver.execute_script(f"document.execCommand('insertText', false, `{escaped_t}`);")
        except Exception:
            pass

    # Enter body - click body area and type
    try:
        body_el = driver.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
        if len(body_el) > 1:
            target = body_el[1]  # Second contenteditable is usually the body
        else:
            target = body_el[0]

        target.click()
        time.sleep(0.5)

        # Insert text paragraph by paragraph
        paragraphs = body_text.split("\n")
        for para in paragraphs:
            escaped = para.replace("\\", "\\\\").replace("`", "'").replace("${", "$ {")
            script = f"""
                document.execCommand('insertText', false, `{escaped}`);
                document.execCommand('insertParagraph');
            """
            driver.execute_script(script)
            time.sleep(0.1)

        print("Body text inserted")
        time.sleep(2)
    except Exception as e:
        print(f"Could not set body: {e}")

    # Try to publish
    try:
        # Click publish/draft button
        publish_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "公開") or contains(text(), "投稿")]'))
        )
        publish_btn.click()
        time.sleep(3)

        # Set tags if tag input exists
        try:
            tag_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="タグ"], input[placeholder*="ハッシュタグ"]')
            for tag in tags:
                tag_input.send_keys(tag)
                tag_input.send_keys("\n")
                time.sleep(0.5)
        except Exception:
            pass

        # Confirm publish
        try:
            confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "投稿") or contains(text(), "公開")]'))
            )
            confirm_btn.click()
            time.sleep(5)
        except Exception:
            pass

        current_url = driver.current_url
        print(f"Published! URL: {current_url}")
        return current_url

    except Exception as e:
        print(f"Publishing step: {e}")
        # Save as draft instead
        try:
            driver.get("https://note.com/notes/new")
            time.sleep(2)
        except Exception:
            pass
        return driver.current_url


def main():
    # Read article
    with open(ARTICLE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title (first # line)
    lines = content.strip().split("\n")
    title = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:]).strip()

    print(f"Article: {title[:60]}...")
    print(f"Body length: {len(body)} chars")

    driver = create_driver()
    try:
        if login_note(driver):
            url = post_article(driver, title, body, TAGS)
            print(f"\nResult URL: {url}")

            # Save URL for tweet
            with open("media/content_drafts/note_url.txt", "w") as f:
                f.write(url)
        else:
            print("Login failed, cannot post")
    finally:
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()
