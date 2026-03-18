"""Post tweet via Selenium browser automation."""
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

TWITTER_EMAIL = "alwayswabisabi@gmail.com"
TWITTER_USERNAME = "shawshank827"
TWITTER_PASSWORD = "PlanB1513t"

TWEET_TEXT = (
    "エルメスのバーキンは持ってるだけで毎月2万円の利益が出る。\n\n"
    "一方コーチは毎月3,700円ずつ溶けてる。\n\n"
    "安いブランドほどコスパが悪いという逆転現象をデータで証明した。\n\n"
    "ブランド品の本当の値段を可視化するアプリ「リセールレンズ」を開発中。\n\n"
    "18ブランド・81モデルのリセールスコアを毎日更新予定。"
)


def main():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--window-size=1280,900")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        # Login
        driver.get("https://x.com/i/flow/login")
        time.sleep(5)

        # Email
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
        )
        email_input.send_keys(TWITTER_EMAIL)
        time.sleep(1)

        # Click Next
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[role="button"]')
        for btn in buttons:
            if btn.text.strip() in ("Next", "次へ"):
                btn.click()
                print("Clicked Next")
                break
        time.sleep(3)

        # Username verification if needed
        try:
            verify_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]'))
            )
            verify_input.send_keys(TWITTER_USERNAME)
            verify_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="ocfEnterTextNextButton"]')
            verify_btn.click()
            time.sleep(3)
            print("Username verified")
        except Exception:
            print("No username verification needed")

        # Password
        pw_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"], input[type="password"]'))
        )
        pw_input.send_keys(TWITTER_PASSWORD)
        time.sleep(1)

        login_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]')
        login_btn.click()
        time.sleep(6)

        print(f"Logged in: {driver.current_url}")

        # Navigate to compose
        driver.get("https://x.com/compose/tweet")
        time.sleep(4)

        # Find compose box
        compose = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"], [role="textbox"]'))
        )
        compose.click()
        time.sleep(1)

        # Insert text
        safe_text = TWEET_TEXT.replace("`", "'")
        driver.execute_script(
            "var el = document.querySelector('[data-testid=\"tweetTextarea_0\"], [role=\"textbox\"]');"
            "el.focus();"
            "document.execCommand('insertText', false, arguments[0]);",
            safe_text
        )
        time.sleep(2)

        # Post
        post_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
        )
        post_btn.click()
        time.sleep(5)

        print(f"Tweet posted! URL: {driver.current_url}")
        driver.save_screenshot("tweet_success.png")
        print("SUCCESS")

    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("debug_twitter.png")
        print(f"URL: {driver.current_url}")
    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
