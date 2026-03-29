from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
FROM  = os.getenv("TWILIO_FROM")   # whatsapp:+14155238886
TO    = os.getenv("TWILIO_TO")     # whatsapp:+91XXXXXXXXXX

MAX_CHARS = 1500  # WhatsApp limit is ~1600, keep buffer

def send_whatsapp(text: str):
    """Send a message, auto-chunking if over limit."""
    chunks = chunk_message(text)
    for i, chunk in enumerate(chunks):
        client.messages.create(
            from_=FROM,
            to=TO,
            body=chunk
        )
        print(f"Sent chunk {i+1}/{len(chunks)}")

def chunk_message(text: str) -> list:
    """Split long text into WhatsApp-safe chunks at paragraph boundaries."""
    if len(text) <= MAX_CHARS:
        return [text]
    
    chunks, current = [], ""
    for para in text.split("\n\n"):
        if len(current) + len(para) + 2 > MAX_CHARS:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para if current else para
    if current:
        chunks.append(current.strip())
    return chunks

def format_report_for_whatsapp(report: str) -> str:
    """Convert markdown report to WhatsApp-friendly format."""
    # WhatsApp supports *bold* and _italic_
    text = report
    text = text.replace("### ", "*").replace("## ", "*")
    text = text.replace("**", "*")   # markdown bold → WhatsApp bold
    text = text.replace("__", "_")   # markdown italic → WhatsApp italic
    return text