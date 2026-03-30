import urllib.request
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAX_CHARS        = 4000  # Telegram limit is 4096


def send_telegram(text: str):
    """Send a message to Telegram, auto-chunking if over limit."""
    chunks = chunk_message(text)
    for i, chunk in enumerate(chunks):
        _send_chunk(chunk)
        print("Telegram chunk " + str(i + 1) + "/" + str(len(chunks)) + " sent.")


def _send_chunk(text: str):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def chunk_message(text: str) -> list:
    """Split long text into Telegram-safe chunks."""
    if len(text) <= MAX_CHARS:
        return [text]
    chunks = []
    current = ""
    for para in text.split("\n\n"):
        if len(current) + len(para) + 2 > MAX_CHARS:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para
    if current:
        chunks.append(current.strip())
    return chunks