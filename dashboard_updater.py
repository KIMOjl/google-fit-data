#!/usr/bin/env python3
"""
Live Data Connector for Dashboard
Fetches real-time Google Fit data and updates dashboard JSON.
"""

import json
import urllib.request
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, "/home/openclaw/.openclaw/workspace/scripts")
from fitness_tracker import get_access_token, get_daily_summary, get_weekly_summary

DASHBOARD_DIR = Path("/home/openclaw/.openclaw/workspace/dashboard")
DATA_FILE = DASHBOARD_DIR / "data.json"

def update_dashboard_data():
    """Fetch live data and save for dashboard consumption."""
    try:
        token = get_access_token()
        
        # Get today's and yesterday's data
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        
        daily = get_daily_summary(token, yesterday)
        weekly = get_weekly_summary(token)
        
        # Build data structure for dashboard
        data = {
            "last_updated": today.isoformat(),
            "daily": {
                "date": daily.get("date"),
                "steps": daily.get("steps", 0),
                "heart_rate_avg": daily.get("heart_rate_avg"),
                "heart_rate_max": daily.get("heart_rate_max"),
                "heart_rate_min": daily.get("heart_rate_min"),
                "sleep_hours": daily.get("sleep_hours", 0),
                "active_minutes": daily.get("active_minutes", 0),
                "calories": daily.get("calories", 0),
                "distance_meters": daily.get("distance_meters", 0),
            },
            "weekly": weekly,
            "status": "live" if daily.get("steps", 0) > 0 else "waiting_for_data"
        }
        
        # Save to JSON
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return f"✅ Dashboard data updated: {data['status']}"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    print(update_dashboard_data())
