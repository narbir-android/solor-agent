import requests, feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os, json
load_dotenv()

RSS_FEEDS = [
    "https://pv-magazine-usa.com/feed/",
    "https://www.solarpowerworldonline.com/feed/",
    "https://www.canarymedia.com/articles/solar/feed.xml",
]

COMPETITORS = {
    "Sunrun":  "https://www.sunrun.com",
    "Tesla Energy": "https://www.tesla.com/energy",
    "Enphase": "https://enphase.com",
    "First Solar": "https://www.firstsolar.com",
}

def fetch_news(max_items=10):
    """Fetch latest solar industry news from RSS feeds."""
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            articles.append({
                "title": entry.get("title",""),
                "summary": entry.get("summary","")[:300],
                "link": entry.get("link",""),
                "published": entry.get("published",""),
                "source": feed.feed.get("title","")
            })
    return articles[:max_items]

def scrape_competitor(name, url):
    """Basic competitor page scrape — extend with CSS selectors per site."""
    try:
        r = requests.get(url, timeout=10,
            headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        # Extract first 500 chars of visible text as a basic signal
        text = " ".join(soup.get_text().split())[:500]
        return {"name": name, "url": url, "snapshot": text}
    except Exception as e:
        return {"name": name, "url": url, "snapshot": f"Error: {e}"}

def collect_all_data():
    news = fetch_news()
    competitors = [scrape_competitor(n,u) for n,u in COMPETITORS.items()]
    return {"news": news, "competitors": competitors}