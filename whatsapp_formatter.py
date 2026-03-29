def build_whatsapp_summary(report: str) -> str:
    """
    Extracts only the TL;DR + Alerts for the morning ping.
    Full report is a follow-up message.
    """
    lines = report.split("\n")
    
    # Extract TL;DR section
    tldr, in_tldr = [], False
    for line in lines:
        if "Quick Summary" in line or "TL;DR" in line:
            in_tldr = True
        elif in_tldr and line.startswith("###"):
            break
        elif in_tldr and line.strip():
            tldr.append(line.strip())

    # Extract Alerts section
    alerts, in_alerts = [], False
    for line in lines:
        if "Alerts" in line and "###" in line:
            in_alerts = True
        elif in_alerts and line.startswith("###"):
            break
        elif in_alerts and line.strip():
            alerts.append(line.strip())

    from datetime import date
    summary = f"""*Solar Market Intel — {date.today()}*

*Quick Summary*
{chr(10).join(tldr[:3])}

*Alerts*
{chr(10).join(alerts[:5]) if alerts else "No critical alerts today."}

_Reply *FULL* for the complete report_"""
    return summary


def send_morning_brief(report: str):
    """Send compact brief first, offer full report on request."""
    from whatsapp import send_whatsapp
    
    # 1. Send compact summary
    summary = build_whatsapp_summary(report)
    send_whatsapp(summary)
    
    # 2. Send full report as follow-up chunks
    import time
    time.sleep(2)
    from whatsapp import format_report_for_whatsapp
    full = format_report_for_whatsapp(report)
    send_whatsapp(f"*Full Report Below*\n\n{full}")