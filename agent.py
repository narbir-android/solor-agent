import json
import os
import urllib.request
from datetime import date
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent?key=" + (GEMINI_API_KEY or "")
)

SYSTEM_PROMPT = (
    "You are an advanced market intelligence AI for the US solar industry. "
    "Produce a daily report with exactly 8 sections.\n\n"
    "RULES:\n"
    "- Be concise but highly insightful.\n"
    "- Only flag meaningful changes vs yesterday.\n"
    "- Alerts must be rare but high-value.\n\n"
    "OUTPUT SECTIONS:\n"
    "### 1. US Solar Industry Update\n"
    "- Key news bullets, market trend, top risk or opportunity\n\n"
    "### 2. Competitor Analysis\n"
    "- Name, Pricing, Services, Recent Updates, Customer Perception\n\n"
    "### 3. Competitive Insights\n"
    "- Why competitors perform better, their strategies, gaps in our offering\n\n"
    "### 4. Actionable Recommendations\n"
    "- 3 to 5 specific business-impact actions\n\n"
    "### 5. Trend Analysis\n"
    "- Changes vs previous reports, pricing trends, growth signals, 30-day prediction\n\n"
    "### 6. Competitor Scoring\n"
    "- Rank each competitor 0-10 on price, service, market presence, sentiment\n\n"
    "### 7. Alerts\n"
    "- Only for price drops, new services, sentiment shifts, aggressive moves\n"
    "- If none write: No critical alerts today.\n\n"
    "### 8. Quick Summary TL;DR\n"
    "- Max 3 bullet points, most critical insights only."
)


def call_gemini(prompt):
    payload = json.dumps({
        "contents": [{
            "parts": [{
                "text": SYSTEM_PROMPT + "\n\n" + prompt
            }]
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]


def build_user_message(raw_data, yesterday, history):
    return (
        "TODAY DATA:\n"
        + json.dumps(raw_data.get("news", []), indent=2)
        + "\n\nCOMPETITORS:\n"
        + json.dumps(raw_data.get("competitors", []), indent=2)
        + "\n\nYESTERDAY SUMMARY:\n"
        + json.dumps(yesterday.get("summary", "No previous report."), indent=2)
        + "\n\nProduce the full 8-section report now."
    )


def run_agent():
    from scraper import collect_all_data
    from memory import get_yesterday_report, get_history, save_report

    print("Fetching live data...")
    raw_data = collect_all_data()

    print("Loading memory...")
    yesterday = get_yesterday_report()
    history = get_history(days=7)

    print("Running AI analysis...")
    report_text = call_gemini(
        build_user_message(raw_data, yesterday, history)
    )
    print("Report generated.")

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    save_report({
        "raw": raw_data,
        "report": report_text,
        "summary": report_text[:500]
    })

    with open("reports/report_" + str(date.today()) + ".md", "w") as f:
        f.write(report_text)

    print("Done.")
    return report_text


if __name__ == "__main__":
    print(run_agent())
