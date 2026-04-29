#!/usr/bin/env python3
"""
Proactive Fitness Alerts for KIMO
Checks Google Fit data and sends alerts based on thresholds.
"""

import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# Import fitness tracker functions
import sys
sys.path.insert(0, "/home/openclaw/.openclaw/workspace/scripts")
from fitness_tracker import get_access_token, get_daily_summary, get_weekly_summary

# Alert thresholds
THRESHOLDS = {
    "steps_low": 5000,
    "steps_goal": 10000,
    "sleep_min": 6,
    "sleep_optimal": 7.5,
    "hr_resting_high": 80,
    "active_min_low": 30,
}

def check_alerts(daily_summary, weekly_summary=None):
    """Check for conditions that warrant an alert."""
    alerts = []
    
    # Steps
    steps = daily_summary.get("steps", 0)
    if steps >= THRESHOLDS["steps_goal"]:
        alerts.append({"type": "success", "message": f"🎉 Step goal crushed! {steps:,} steps today"})
    elif steps < THRESHOLDS["steps_low"]:
        alerts.append({"type": "warning", "message": f"⚠️ Only {steps:,} steps so far — time to move!"})
    
    # Sleep
    sleep = daily_summary.get("sleep_hours", 0)
    if sleep and sleep < THRESHOLDS["sleep_min"]:
        alerts.append({"type": "warning", "message": f"😴 Only {sleep}h sleep last night — prioritize rest tonight"})
    elif sleep and sleep >= THRESHOLDS["sleep_optimal"]:
        alerts.append({"type": "success", "message": f"✅ Solid {sleep}h sleep — recovery on point"})
    
    # Heart Rate
    hr_avg = daily_summary.get("heart_rate_avg")
    if hr_avg and hr_avg > THRESHOLDS["hr_resting_high"]:
        alerts.append({"type": "warning", "message": f"⚠️ Elevated resting HR ({hr_avg} bpm) — consider a rest day"})
    
    # Active minutes
    active = daily_summary.get("active_minutes", 0)
    if active < THRESHOLDS["active_min_low"]:
        alerts.append({"type": "warning", "message": f"🔥 Only {active}m active today — aim for 30m minimum"})
    elif active >= 60:
        alerts.append({"type": "success", "message": f"🔥 {active}m active — great work!"})
    
    # Training Load Intelligence
    training_load = 0
    if daily_summary.get("steps"):
        training_load += min(daily_summary["steps"] / 1000, 20)
    if daily_summary.get("active_minutes"):
        training_load += daily_summary["active_minutes"] * 0.5
    if daily_summary.get("distance_meters"):
        training_load += daily_summary["distance_meters"] / 1000 * 2
    
    if training_load > 50 and sleep < 6:
        alerts.append({"type": "critical", "message": f"🚨 HIGH FATIGUE RISK: Heavy training ({round(training_load,1)}) + poor sleep. MANDATORY rest day tomorrow."})
    elif training_load > 50:
        alerts.append({"type": "warning", "message": f"⚡ High training load ({round(training_load,1)}) — prioritize 8h+ sleep tonight"})
    
    # Recovery Status
    if hr_avg and hr_avg < 65 and sleep and sleep > 7:
        alerts.append({"type": "success", "message": "🟢 Recovery status: EXCELLENT. Ready for hard training."})
    elif hr_avg and hr_avg > 75 and sleep and sleep < 6:
        alerts.append({"type": "critical", "message": "🚨 RECOVERY COMPROMISED: Elevated HR + poor sleep. Light activity only today."})
    
    # Cycling-specific
    distance = daily_summary.get("distance_meters", 0)
    if distance > 50000:  # 50km+
        km = distance / 1000
        alerts.append({"type": "info", "message": f"🚴 Long ride: {km:.1f}km. Ensure 60g carbs + 20g protein within 30min."})
    
    # Weekly trend context
    if weekly_summary:
        avg_steps = weekly_summary.get("avg_steps", 0)
        if steps > avg_steps * 1.5:
            alerts.append({"type": "warning", "message": f"📈 50%+ above your weekly avg steps. Monitor fatigue."})
        elif steps < avg_steps * 0.5:
            alerts.append({"type": "info", "message": f"📉 50% below weekly avg. Rest day or need to move more?"})
    
    # Consistency score
    if weekly_summary and weekly_summary.get("days", 0) >= 5:
        consistency = sum(1 for d in weekly_summary["daily_breakdown"].values() if d["steps"] > 5000) / weekly_summary["days"]
        if consistency < 0.6:
            alerts.append({"type": "warning", "message": f"📊 Consistency: Only {round(consistency*100)}% of days hit 5k steps. Build the habit."})
        elif consistency > 0.85:
            alerts.append({"type": "success", "message": f"📊 Consistency: {round(consistency*100)}% of days active. Solid routine!"})
    
    return alerts

def format_alert_message(alerts, summary):
    """Format alerts into a message."""
    if not alerts:
        return None
    
    lines = [f"⚡ **Fitness Alert — {summary['date']}**", ""]
    
    # Sort by severity
    severity_order = {"critical": 0, "warning": 1, "info": 2, "success": 3}
    alerts.sort(key=lambda x: severity_order.get(x["type"], 99))
    
    for alert in alerts:
        lines.append(alert["message"])
    
    lines.append("")
    lines.append(f"👟 Steps: {summary['steps']:,} | 😴 Sleep: {summary['sleep_hours']}h | ❤️ HR: {summary['heart_rate_avg']} bpm")
    
    # Add intelligent action items
    lines.append("")
    lines.append("**🎯 Action Items:**")
    
    critical_alerts = [a for a in alerts if a["type"] == "critical"]
    if critical_alerts:
        lines.append("• **IMMEDIATE:** Follow recovery protocol. No hard training today.")
        lines.append("• Hydrate aggressively (3L+ water + electrolytes)")
        lines.append("• Aim for 9h sleep tonight minimum")
    
    if summary["steps"] < 5000:
        lines.append("• 20-min walk after next meal")
    
    if summary.get("sleep_hours", 0) < 6:
        lines.append("• No screens 1h before bed tonight")
        lines.append("• Magnesium + melatonin protocol")
    
    if summary.get("distance_meters", 0) > 50000:
        lines.append("• Post-ride nutrition: 60g carbs + 20g protein NOW")
    
    return "\n".join(lines)

if __name__ == "__main__":
    token = get_access_token()
    summary = get_daily_summary(token)
    alerts = check_alerts(summary)
    
    if alerts:
        message = format_alert_message(alerts, summary)
        print(message)
    else:
        print("No alerts today — all metrics look good!")
