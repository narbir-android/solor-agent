import json
import os
import urllib.request
from datetime import date
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-lite:generateContent?key=" + GEMINI_API_KEY
)



SYSTEM_PROMPT = (
    "You are an advanced market intelligence AI specialized in the US solar "
    "pre-installation and services industry. This includes companies providing: "
    "site surveys, plan sets, PE stamps, permitting, PTO (Permission to Operate), "
    "interconnection applications, HOA approvals, and utility coordination.\n\n"

    "RULES:\n"
    "- Be concise but highly insightful.\n"
    "- Only flag meaningful changes vs yesterday.\n"
    "- Alerts must be rare but high-value.\n"
    "- Focus on pricing, turnaround time, and service quality differences.\n\n"

    "OUTPUT SECTIONS:\n"

    "### 1. US Solar Services Industry Update\n"
    "- Key news affecting permitting, PTO, surveys, plan sets\n"
    "- Regulatory changes impacting pre-installation services\n"
    "- Top opportunity or risk for solar service providers\n\n"

    "### 2. Competitor Analysis\n"
    "For each competitor provide:\n"
    "- Name | Service type | Pricing | Turnaround time | Recent updates\n\n"

    "### 3. Competitive Insights\n"
    "- Why competitors are winning (speed, price, technology)\n"
    "- Strategies they are using\n"
    "- Gaps in our offering\n\n"

    "### 4. Actionable Recommendations\n"
    "- 3 to 5 specific actions to improve our solar services business\n"
    "- Focus on turnaround time, pricing, automation, customer experience\n\n"

    "### 5. Trend Analysis\n"
    "- Changes in permitting timelines across US states\n"
    "- PTO approval rate trends\n"
    "- Technology adoption in plan sets and PE stamps\n"
    "- 30-day market direction prediction\n\n"

    "### 6. Competitor Scoring\n"
    "Rank each competitor 0-10 on:\n"
    "- Price competitiveness | Turnaround speed | Service quality | "
    "Technology | Customer satisfaction\n\n"

    "### 7. Alerts\n"
    "- Only for: major price drops, new service launches, "
    "regulatory changes affecting permits/PTO, aggressive competitor moves\n"
    "- If none write: No critical alerts today.\n\n"

    "### 8. Quick Summary TL;DR\n"
    "- Max 3 bullet points, most critical insights only."
)
def call_gemini(prompt):
    payload = json.dumps({
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": 4000,
            "temperature": 0.7
        }
    }).encode("utf-8")
    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise Exception(f"Gemini error: {e}")

def build_user_message(raw_data):
    return (
        "TODAY DATA:\n"
        + json.dumps(raw_data.get("news", []), indent=2)
        + "\n\nCOMPETITORS:\n"
        + json.dumps(raw_data.get("competitors", []), indent=2)
        + "\n\nProduce the full analyst report now including the comparison table and WhatsApp summary."
    )
def run_agent():
    from scraper import collect_all_data
    from memory import get_yesterday_report, get_history, save_report
    print("Fetching live data...")
    raw_data = collect_all_data()
    print("Loading memory...")
    yesterday = get_yesterday_report()
    history = get_history(days=7)
    report_text = call_gemini(
        build_user_message(raw_data)
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
