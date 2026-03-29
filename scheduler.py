import logging
import re
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)


def clean_text(text):
    """Remove control characters that WhatsApp rejects."""
    # Remove all control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def daily_job():
    log.info("Starting solar agent run...")
    try:
        from agent import run_agent
        report = run_agent()

        # Clean text before sending
        safe_report = clean_text(report)
        preview = clean_text("*Solar Agent Report*\n\n" + safe_report[:400])

        try:
            from whatsapp import send_whatsapp
            send_whatsapp(preview)
            log.info("WhatsApp sent.")
        except Exception as e:
            log.error("WhatsApp failed: " + str(e))

        try:
            from report import send_report_email
            send_report_email(report)
            log.info("Email sent.")
        except Exception as e:
            log.error("Email failed: " + str(e))

        log.info("Run complete.")

    except Exception as e:
        log.error("Agent failed: " + str(e))
        try:
            from whatsapp import send_whatsapp
            send_whatsapp("AGENT ERROR:\n" + str(e))
        except Exception:
            pass


# IST = UTC+5:30 → 7am IST = 1:30am UTC
ist = pytz.timezone("Asia/Kolkata")

scheduler = BlockingScheduler()

# Production: every day at 7am IST
# scheduler.add_job(
#     daily_job,
#     CronTrigger(hour=7, minute=0, timezone=ist)
# )

# For testing uncomment this and comment the line above:
scheduler.add_job(daily_job, "interval", minutes=1)

log.info("Scheduler started. Running daily at 7:00 AM IST.")
scheduler.start()
