import json, os
from datetime import datetime, timedelta

MEMORY_DIR = "data"

def today_key():
    return datetime.now().strftime("%Y-%m-%d")

def yesterday_key():
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def save_report(report: dict):
    """Save today's report to disk."""
    path = f"{MEMORY_DIR}/{today_key()}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved report: {path}")

def load_report(date_key: str) -> dict:
    """Load a report by date key (YYYY-MM-DD)."""
    path = f"{MEMORY_DIR}/{date_key}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def get_yesterday_report() -> dict:
    return load_report(yesterday_key())

def get_history(days=7) -> list:
    """Load last N days of reports for trend analysis."""
    history = []
    for i in range(1, days+1):
        key = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        r = load_report(key)
        if r:
            history.append({"date": key, "report": r})
    return history