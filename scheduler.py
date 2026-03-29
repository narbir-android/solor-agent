import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)


def daily_job():
    log.info("Starting solar agent run...")
    try:
        from agent import run_agent
        report = run_agent()

        try:
            from whatsapp import send_whatsapp
            send_whatsapp("*Solar Agent Test*\n\n" + report[:500])
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
scheduler.add_job(
    daily_job,
    CronTrigger(hour=7, minute=0, timezone=ist)
)

log.info("Scheduler started. Running daily at 7:00 AM IST.")
scheduler.start()
