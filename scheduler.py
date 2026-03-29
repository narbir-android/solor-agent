import logging
import os
from apscheduler.schedulers.blocking import BlockingScheduler

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

        # ── WhatsApp ──────────────────────────────
        try:
            from whatsapp import send_whatsapp
            send_whatsapp("*Solar Agent Test*\n\n" + report[:500])
            log.info("WhatsApp sent.")
        except Exception as e:
            log.error(f"WhatsApp failed: {e}")

        # ── Email (optional backup) ───────────────
        try:
            from report import send_report_email
            send_report_email(report)
            log.info("Email sent.")
        except Exception as e:
            log.error(f"Email failed: {e}")

        log.info("Run complete.")

    except Exception as e:
        log.error(f"Agent failed: {e}")
        # Notify via WhatsApp if agent itself crashes
        try:
            from whatsapp import send_whatsapp
            send_whatsapp(f"AGENT ERROR:\n{str(e)}")
        except Exception:
            pass


scheduler = BlockingScheduler()

# ── CHANGE THIS LINE TO SWITCH BETWEEN TEST AND PRODUCTION ──
# Every 1 minute  (for testing):
scheduler.add_job(daily_job, "interval", minutes=1)

# Every day at 7am (for production — uncomment when ready):
# scheduler.add_job(daily_job, "cron", hour=7, minute=0)

log.info("Scheduler started. Running every 1 minute.")
scheduler.start()
