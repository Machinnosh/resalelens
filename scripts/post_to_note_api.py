"""Post article to note.com using HTTP API (adapted from money-chaos-japan)."""

import sys
import io
import os
import re
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests

NOTE_EMAIL = os.environ.get("NOTE_EMAIL", "alwayswabisabi@gmail.com")
NOTE_PASSWORD = os.environ.get("NOTE_PASSWORD", "PlanB1513t")

ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "..", "media", "content_drafts", "note_final.md")
TAGS = ["ブランド", "リセール", "エルメス", "シャネル", "バッグ", "個人開発"]


def markdown_to_note_html(md_text: str) -> str:
    """Convert markdown to note.com HTML body format."""
    lines = md_text.strip().split("\n")
    html_parts = []
    for line in lines:
        line = line.rstrip()
        if not line:
            html_parts.append("<p><br></p>")
        elif line.startswith("### "):
            html_parts.append(f"<h4>{line[4:]}</h4>")
        elif line.startswith("## "):
            html_parts.append(f"<h3>{line[3:]}</h3>")
        elif line.startswith("# "):
            continue  # Title handled separately
        elif line.startswith("---"):
            html_parts.append("<hr>")
        elif line.startswith("- "):
            html_parts.append(f"<p>・{line[2:]}</p>")
        else:
            # Escape bold markdown to note-friendly format
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            html_parts.append(f"<p>{text}</p>")
    return "\n".join(html_parts)


def login_session() -> requests.Session | None:
    """Login to note.com and get session."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
    })

    try:
        resp = session.post(
            "https://note.com/api/v1/sessions/sign_in",
            json={"login": NOTE_EMAIL, "password": NOTE_PASSWORD},
            timeout=15,
        )
        if resp.status_code in (200, 201):
            print(f"[note] Login success (status {resp.status_code})")
            return session
        else:
            print(f"[note] Login failed: {resp.status_code} {resp.text[:300]}")
    except Exception as e:
        print(f"[note] Login error: {e}")
    return None


def post_article(session: requests.Session, title: str, body_html: str,
                 tags: list[str], publish: bool = True) -> dict:
    """Post article via note.com API."""
    post_urls = [
        "https://note.com/api/v3/text_notes",
        "https://note.com/api/v2/text_notes",
        "https://note.com/api/v1/text_notes",
    ]

    payload = {
        "name": title,
        "body": body_html,
        "status": "published" if publish else "draft",
        "tag_names": tags,
        "template_key": "",
    }

    for post_url in post_urls:
        try:
            resp = session.post(post_url, json=payload, timeout=30)
            if resp.status_code in (200, 201):
                result = resp.json()
                print(f"[note] Article posted via {post_url}")
                return {"run": "success", "data": result}
            else:
                print(f"[note] POST {post_url}: {resp.status_code} {resp.text[:300]}")
        except Exception as e:
            print(f"[note] POST {post_url} failed: {e}")

    return {"run": "failed", "error": "All API endpoints failed"}


def main():
    # Read article
    with open(ARTICLE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    title = lines[0].lstrip("# ").strip()
    body_md = "\n".join(lines[1:]).strip()
    body_html = markdown_to_note_html(body_md)

    print(f"Title: {title[:60]}...")
    print(f"Body HTML length: {len(body_html)} chars")

    # Login
    session = login_session()
    if not session:
        print("FAILED: Could not login to note.com")
        return

    # Post article (published)
    result = post_article(session, title, body_html, TAGS, publish=True)
    print(f"\nResult: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")

    # Extract note URL
    if result.get("run") == "success":
        data = result.get("data", {})
        note_data = data.get("data", data)
        note_key = note_data.get("key", note_data.get("note_key", ""))
        if note_key:
            note_url = f"https://note.com/shawshank827/n/{note_key}"
        else:
            note_url = f"https://note.com/shawshank827"
        print(f"\nNote URL: {note_url}")

        # Save URL for tweet
        url_file = os.path.join(os.path.dirname(__file__), "..", "media", "content_drafts", "note_url.txt")
        with open(url_file, "w") as f:
            f.write(note_url)
        print(f"URL saved to: {url_file}")


if __name__ == "__main__":
    main()
