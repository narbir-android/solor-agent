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
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def daily_job():
    log.info("Starting solar agent run...")
    try:
        from agent import run_agent
        report = run_agent()

        safe_report = clean_text(report)
        preview = clean_text("*Solar Agent Report*\n\n" + safe_report[:400])

        try:
            from whatsapp import send_whatsapp
            # ✅ CHANGE 1 — log the message before sending
            log.info("Sending WhatsApp message:\n" + preview)
            send_whatsapp(preview)
            log.info("WhatsApp sent.")
        except Exception as e:
            # ✅ CHANGE 2 — log the failed message too
            log.error("WhatsApp failed: " + str(e))
            log.error("Failed message was:\n" + preview)

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
            error_msg = clean_text("AGENT ERROR:\n" + str(e))
            # ✅ CHANGE 3 — log error message before sending
            log.info("Sending error WhatsApp:\n" + error_msg)
            send_whatsapp(error_msg)
        except Exception:
            pass


ist = pytz.timezone("Asia/Kolkata")
scheduler = BlockingScheduler()

# TESTING — every 1 minute
scheduler.add_job(daily_job, "interval", minutes=1)

# PRODUCTION — uncomment when ready
# scheduler.add_job(daily_job, CronTrigger(hour=7, minute=0, timezone=ist))

log.info("Scheduler started. Running every 1 minute.")
scheduler.start()
