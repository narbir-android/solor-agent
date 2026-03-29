from agent import run_agent
from report import send_report_email, check_and_send_alerts
from whatsapp_formatter import send_morning_brief
import logging, os

log = logging.getLogger(__name__)

def daily_job():
    log.info("Starting daily solar intelligence run...")
    try:
        report = run_agent()

        # --- Email (keep as backup) ---
        send_report_email(report)

        # --- WhatsApp (primary delivery) ---
        send_morning_brief(report)
        
        # --- Alerts via WhatsApp ---
        check_and_send_whatsapp_alerts(report)

        log.info("Daily run complete. Report sent via WhatsApp + Email.")

    except Exception as e:
        log.error(f"Agent failed: {e}")
        # Send failure alert to WhatsApp
        from whatsapp import send_whatsapp
        send_whatsapp(f"AGENT ERROR at {__import__('datetime').datetime.now()}\n{str(e)}")

def check_and_send_whatsapp_alerts(report: str):
    """Send instant WhatsApp alert if critical change detected."""
    from whatsapp import send_whatsapp
    if "ALERT TYPE:" in report:
        lines = [l for l in report.split("\n") if "ALERT" in l.upper()]
        alert_text = "*CRITICAL ALERT*\n" + "\n".join(lines[:8])
        send_whatsapp(alert_text)
        log.info("Alert sent via WhatsApp.")