import anthropic
import json
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
You are an advanced market intelligence AI specialized in the US solar industry.
Your role is to act as a fully autonomous business analyst, competitor strategist,
and market monitoring agent.

You produce a structured daily report with exactly 8 sections.

RULES:
- Be concise but highly insightful. No generic statements.
- Only flag meaningful changes vs yesterday. Ignore noise.
- Alerts must be rare but high-value (price drops, new services, sentiment shifts).
- Always compare with historical data before concluding.

OUTPUT FORMAT (use these exact headers):

### 1. US Solar Industry Update
- Bullet point key news (last 24h)
- Market trend summary
- Top opportunity or risk

### 2. Competitor Analysis
For each competitor:
Name | Pricing Summary | Services | Recent Updates | Customer Perception

### 3. Competitive Insights
- Why competitors are performing better
- Strategies they are using
- Gaps in our offering

### 4. Actionable Recommendations
- 3-5 specific, business-impact actions

### 5. Trend Analysis
- Changes vs previous reports
- Pricing trends
- Competitor growth/decline signals
- 30-day market direction prediction

### 6. Competitor Scoring
Rank each competitor (0-10) on:
Price competitiveness | Service quality | Market presence | Customer sentiment

### 7. Alerts
Only trigger if: significant price drop, new service launch,
major sentiment shift, or aggressive competitor move.
Format: ALERT TYPE | COMPETITOR | CHANGE | IMPACT | ACTION
If none: write exactly "No critical alerts today."

### 8. Quick Summary (TL;DR)
- Max 3 bullet points. Most critical insights only.
"""


def build_user_message(raw_data: dict, yesterday: dict, history: list) -> str:
    return f"""
## TODAY'S DATA
### Industry News
{json.dumps(raw_data.get('news', []), indent=2)}

### Competitor Data
{json.dumps(raw_data.get('competitors', []), indent=2)}

## HISTORICAL CONTEXT
### Yesterday's Report Summary
{json.dumps(yesterday.get('summary', 'No previous report available.'), indent=2)}

### Recent History Dates
{json.dumps([h['date'] for h in history], indent=2)}

## YOUR TASK
Produce the full 8-section solar market intelligence report.
Compare today's data with historical context.
Highlight ONLY meaningful changes.
"""


def run_agent():
    from scraper import collect_all_data
    from memory import get_yesterday_report, get_history, save_report

    print("Fetching live data...")
    raw_data = collect_all_data()

    print("Loading memory...")
    yesterday = get_yesterday_report()
    history = get_history(days=7)

    print("Running AI analysis...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": build_user_message(raw_data, yesterday, history)
        }]
    )

    report_text = message.content[0].text
    print("Report generated successfully.")

    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    save_report({
        "raw": raw_data,
        "report": report_text,
        "summary": report_text[:500]
    })

    report_filename = f"reports/report_{date.today()}.md"
    with open(report_filename, "w") as f:
        f.write(report_text)

    print(f"Report saved to {report_filename}")
    return report_text


if __name__ == "__main__":
    print(run_agent())