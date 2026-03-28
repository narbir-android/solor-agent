from apscheduler.schedulers.blocking import BlockingScheduler
from agent import run_agent
from report import send_report_email, check_and_send_alerts

def daily_job():
    print("Starting daily solar intelligence run...")
    report = run_agent()
    send_report_email(report)
    check_and_send_alerts(report)
    print("Done.")

scheduler = BlockingScheduler()
scheduler.add_job(daily_job, "cron", hour=7, minute=0)

print("Solar agent scheduler started. Running daily at 7:00 AM.")
scheduler.start()

# ---- OR use cron (Linux/Mac) ----
# Add to crontab with: crontab -e
# 0 7 * * * /path/to/venv/bin/python /path/to/solar-agent/agent.py >> /path/to/logs/agent.log 2>&1