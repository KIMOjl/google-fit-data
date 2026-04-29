#!/usr/bin/env python3
"""
Google Fit Data Fetcher + Reporter
Fetches fitness data from Google Fit API and generates summaries.
"""

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from env_utils import load_dotenv

load_dotenv()

TOKEN_PATH = Path(os.environ.get("TOKEN_PATH", "credentials/google-fit-token.json"))
TOKEN_URI = "https://oauth2.googleapis.com/token"
SLEEP_ACTIVITY_TYPE = 72
SLEEP_STAGE_VALUES = {2, 4, 5, 6}

def load_tokens():
    with open(TOKEN_PATH) as f:
        return json.load(f)

def refresh_access_token(tokens):
    """Refresh the access token using the refresh token."""
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise ValueError("No refresh token available")
    
    data = urllib.parse.urlencode({
        "refresh_token": refresh_token,
        "client_id": tokens.get("client_id") or os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": tokens.get("client_secret") or os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        "grant_type": "refresh_token",
    }).encode()
    
    req = urllib.request.Request(tokens.get("token_uri", TOKEN_URI), data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    with urllib.request.urlopen(req) as resp:
        new_tokens = json.loads(resp.read())
        # Preserve fields that are not returned in refresh responses.
        for key in ("refresh_token", "client_id", "client_secret", "token_uri", "scopes"):
            if tokens.get(key) and not new_tokens.get(key):
                new_tokens[key] = tokens[key]
        
        # Save updated tokens
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            json.dump(new_tokens, f, indent=2)
        
        return new_tokens

def get_access_token():
    """Get valid access token, refreshing if needed."""
    tokens = load_tokens()
    # For simplicity, we'll refresh proactively. In production, check expiry.
    return refresh_access_token(tokens)["access_token"]

def to_utc(dt):
    """Return a timezone-aware UTC datetime."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def to_millis(dt):
    """Convert a datetime to Unix milliseconds."""
    return int(to_utc(dt).timestamp() * 1000)

def format_rfc3339(dt):
    """Format a datetime for Google Fit session queries."""
    return to_utc(dt).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def query_fitness_data(access_token, start_time, end_time, data_types):
    """Query Google Fit for aggregated data."""
    aggregate_by = []
    for dt in data_types:
        if dt == "steps":
            aggregate_by.append({"dataTypeName": "com.google.step_count.delta"})
        elif dt == "heart_rate":
            aggregate_by.append({"dataTypeName": "com.google.heart_rate.bpm"})
        elif dt == "sleep":
            aggregate_by.append({"dataTypeName": "com.google.sleep.segment"})
        elif dt == "active_minutes":
            aggregate_by.append({"dataTypeName": "com.google.active_minutes"})
        elif dt == "calories":
            aggregate_by.append({"dataTypeName": "com.google.calories.expended"})
        elif dt == "distance":
            aggregate_by.append({"dataTypeName": "com.google.distance.delta"})
    
    body = {
        "aggregateBy": aggregate_by,
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": to_millis(start_time),
        "endTimeMillis": to_millis(end_time),
    }
    
    req = urllib.request.Request(
        "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
        data=json.dumps(body).encode(),
        method="POST",
    )
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def extract_value(point, value_type="intVal"):
    """Extract a value from a data point."""
    if not point or "value" not in point:
        return None
    for v in point["value"]:
        if value_type in v:
            return v[value_type]
    return None

def parse_sleep_data(points):
    """Parse sleep stages and calculate total actual sleep time."""
    intervals = []
    for point in points:
        sleep_stage = extract_value(point, "intVal")
        if sleep_stage not in SLEEP_STAGE_VALUES:
            continue
        start = int(point["startTimeNanos"]) // 1_000_000
        end = int(point["endTimeNanos"]) // 1_000_000
        intervals.append((start, end))
    
    hours = total_interval_hours(intervals)
    return round(hours, 1)

def total_interval_hours(intervals):
    """Merge overlapping intervals and return the total duration in hours."""
    if not intervals:
        return 0

    merged = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    total_ms = sum(end - start for start, end in merged)
    return total_ms / (1000 * 60 * 60)

def list_sleep_sessions(access_token, start_time, end_time):
    """List Google Fit sleep sessions for the given UTC interval."""
    sessions = []
    page_token = None

    while True:
        params = {
            "startTime": format_rfc3339(start_time),
            "endTime": format_rfc3339(end_time),
            "activityType": SLEEP_ACTIVITY_TYPE,
        }
        if page_token:
            params["pageToken"] = page_token

        url = "https://www.googleapis.com/fitness/v1/users/me/sessions?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, method="GET")
        req.add_header("Authorization", f"Bearer {access_token}")

        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())

        sessions.extend(result.get("session", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            return sessions

def aggregate_sleep_session(access_token, session):
    """Aggregate sleep segment details for a single Google Fit sleep session."""
    start_ms = int(session["startTimeMillis"])
    end_ms = int(session["endTimeMillis"])
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.sleep.segment"}],
        "startTimeMillis": start_ms,
        "endTimeMillis": end_ms,
    }

    req = urllib.request.Request(
        "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
        data=json.dumps(body).encode(),
        method="POST",
    )
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())

    points = []
    for bucket in result.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            points.extend(dataset.get("point", []))

    if points:
        return parse_sleep_data(points)

    return round((end_ms - start_ms) / (1000 * 60 * 60), 1)

def get_sleep_hours_by_day(access_token, start_time, end_time):
    """Return sleep hours keyed by the UTC date when each sleep session ended."""
    query_start = start_time - timedelta(hours=12)
    query_end = end_time
    start_ms = to_millis(start_time)
    end_ms = to_millis(end_time)
    sleep_by_day = {}

    for session in list_sleep_sessions(access_token, query_start, query_end):
        session_end_ms = int(session.get("endTimeMillis", 0))
        if not start_ms <= session_end_ms <= end_ms:
            continue

        day = datetime.fromtimestamp(session_end_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        sleep_by_day[day] = sleep_by_day.get(day, 0) + aggregate_sleep_session(access_token, session)

    return {day: round(hours, 1) for day, hours in sleep_by_day.items()}

def get_sleep_hours(access_token, start_time, end_time):
    """Return total sleep hours for sleep sessions ending in the interval."""
    sleep_by_day = get_sleep_hours_by_day(access_token, start_time, end_time)
    return round(sum(sleep_by_day.values()), 1)

def get_daily_summary(access_token, date=None):
    """Get a full daily fitness summary for a specific date."""
    if date is None:
        date = datetime.utcnow() - timedelta(days=1)  # Yesterday by default
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    result = query_fitness_data(
        access_token, start, end,
        ["steps", "heart_rate", "active_minutes", "calories", "distance"]
    )
    
    summary = {
        "date": date.strftime("%Y-%m-%d"),
        "steps": 0,
        "heart_rate_avg": None,
        "heart_rate_max": None,
        "heart_rate_min": None,
        "sleep_hours": 0,
        "active_minutes": 0,
        "calories": 0,
        "distance_meters": 0,
    }
    
    for bucket in result.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            data_type = dataset.get("dataSourceId", "")
            points = dataset.get("point", [])
            
            if "step_count" in data_type:
                for point in points:
                    val = extract_value(point, "intVal")
                    if val:
                        summary["steps"] += val
            
            elif "heart_rate" in data_type and "resting" not in data_type:
                hr_values = [extract_value(p, "fpVal") for p in points if extract_value(p, "fpVal")]
                if hr_values:
                    summary["heart_rate_avg"] = round(sum(hr_values) / len(hr_values), 1)
                    summary["heart_rate_max"] = round(max(hr_values), 1)
                    summary["heart_rate_min"] = round(min(hr_values), 1)
            
            elif "active_minutes" in data_type:
                for point in points:
                    val = extract_value(point, "intVal")
                    if val:
                        summary["active_minutes"] += val
            
            elif "calories" in data_type:
                for point in points:
                    val = extract_value(point, "fpVal")
                    if val:
                        summary["calories"] += val
            
            elif "distance" in data_type:
                for point in points:
                    val = extract_value(point, "fpVal")
                    if val:
                        summary["distance_meters"] += val
    
    try:
        summary["sleep_hours"] = get_sleep_hours(access_token, start, end)
    except Exception as e:
        summary["sleep_error"] = str(e)

    return summary

def format_summary(summary):
    """Format a summary into a readable message."""
    lines = [
        f"📊 **Fitness Summary — {summary['date']}**",
        "",
        f"👟 Steps: {summary['steps']:,}",
    ]
    
    if summary["heart_rate_avg"]:
        lines.append(f"❤️ Heart Rate: {summary['heart_rate_avg']} bpm (max {summary['heart_rate_max']}, min {summary['heart_rate_min']})")
    
    if summary["sleep_hours"]:
        lines.append(f"😴 Sleep: {summary['sleep_hours']}h")
    elif summary.get("sleep_error"):
        lines.append(f"Sleep: unavailable ({summary['sleep_error']})")
    
    if summary["active_minutes"]:
        lines.append(f"🔥 Active Minutes: {summary['active_minutes']}")
    
    if summary["calories"]:
        lines.append(f"🔥 Calories: {summary['calories']:.0f} kcal")
    
    if summary["distance_meters"]:
        km = summary["distance_meters"] / 1000
        lines.append(f"📏 Distance: {km:.1f} km")
    
    # Add insights
    lines.append("")
    lines.append("**💡 Insights:**")
    
    if summary["steps"] >= 10000:
        lines.append("✅ Step goal crushed!")
    elif summary["steps"] >= 5000:
        lines.append("😐 Halfway there on steps")
    else:
        lines.append("⚠️ Low step count — time to move!")
    
    if summary["sleep_hours"]:
        if summary["sleep_hours"] < 6:
            lines.append("⚠️ Sleep deprived — prioritize rest tonight")
        elif summary["sleep_hours"] >= 7:
            lines.append("✅ Good sleep duration")
    
    if summary["heart_rate_avg"] and summary["heart_rate_avg"] > 80:
        lines.append("⚠️ Elevated resting HR — consider a rest day")
    
    # Training Load Analysis
    lines.append("")
    lines.append("**🏋️ Training Intelligence:**")
    
    # Calculate training load score
    training_load = 0
    if summary["steps"]:
        training_load += min(summary["steps"] / 1000, 20)  # Cap at 20 points
    if summary["active_minutes"]:
        training_load += summary["active_minutes"] * 0.5
    if summary["distance_meters"]:
        training_load += summary["distance_meters"] / 1000 * 2
    
    training_load = round(training_load, 1)
    
    if training_load > 50:
        lines.append(f"🔥 High training load ({training_load}) — ensure proper recovery tonight")
    elif training_load > 30:
        lines.append(f"⚡ Solid training load ({training_load}) — good stimulus")
    elif training_load > 10:
        lines.append(f"😐 Moderate training load ({training_load}) — room for more")
    else:
        lines.append(f"💤 Low training load ({training_load}) — consider a workout")
    
    # Recovery recommendations
    if summary["heart_rate_avg"] and summary["heart_rate_avg"] > 75 and summary["sleep_hours"] and summary["sleep_hours"] < 6:
        lines.append("🚨 **Recovery Alert:** Elevated HR + poor sleep = high fatigue. Take a rest day or do light activity only.")
    elif summary["heart_rate_avg"] and summary["heart_rate_avg"] < 65 and summary["sleep_hours"] and summary["sleep_hours"] > 7:
        lines.append("🟢 **Recovery Status:** Good. HR and sleep suggest you're ready to train.")
    
    # Cycling-specific insights
    if summary["distance_meters"] and summary["distance_meters"] > 10000:
        km = summary["distance_meters"] / 1000
        lines.append(f"🚴 Cycling detected: {km:.1f}km logged. Check if this was structured training or commuting.")
        if km > 50:
            lines.append("💡 Long ride day — prioritize carbs and protein within 30min post-ride")
    
    # Weekly context placeholder
    lines.append("")
    lines.append("**📊 Trend Analysis:**")
    lines.append("📈 Compare to your 7-day average for context (weekly report on Mondays)")
    
    # Actionable recommendations
    lines.append("")
    lines.append("**🎯 Recommendations:**")
    
    if summary["steps"] < 5000 and summary["active_minutes"] < 20:
        lines.append("• Take a 20-min walk after your next meal")
        lines.append("• Set a movement alarm every hour")
    
    if summary["sleep_hours"] and summary["sleep_hours"] < 6:
        lines.append("• Aim for 7-8h tonight — no screens 1h before bed")
        lines.append("• Consider magnesium supplement before sleep")
    
    if summary["heart_rate_avg"] and summary["heart_rate_avg"] > 80:
        lines.append("• Skip high-intensity today — do yoga or light cardio")
        lines.append("• Check hydration and electrolyte balance")
    
    # Add visual indicators
    lines.append("")
    lines.append("STEP PROGRESS:")
    step_pct = min(summary['steps'] / 10000, 1)
    bar = "█" * int(step_pct * 30) + "░" * (30 - int(step_pct * 30))
    lines.append(f"[{bar}] {step_pct*100:.0f}%")
    
    if summary['sleep_hours'] and summary['sleep_hours'] > 0:
        lines.append("")
        lines.append("SLEEP QUALITY:")
        sleep_pct = min(summary['sleep_hours'] / 8, 1)
        bar = "█" * int(sleep_pct * 30) + "░" * (30 - int(sleep_pct * 30))
        lines.append(f"[{bar}] {sleep_pct*100:.0f}%")
    
    lines.append("")
    lines.append("=" * 50)
    if summary.get("sleep_error"):
        lines.append("")
        lines.append(f"Sleep unavailable: {summary['sleep_error']}")
    
    return "\n".join(lines)

def get_weekly_summary(access_token):
    """Get a 7-day rolling summary."""
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    
    result = query_fitness_data(
        access_token, start, end,
        ["steps", "heart_rate", "active_minutes", "calories"]
    )
    
    daily = {}
    for bucket in result.get("bucket", []):
        day_start = int(bucket["startTimeMillis"]) // 1000
        day = datetime.utcfromtimestamp(day_start).strftime("%Y-%m-%d")
        
        if day not in daily:
            daily[day] = {"steps": 0, "sleep_hours": 0, "active_minutes": 0, "calories": 0}
        
        for dataset in bucket.get("dataset", []):
            data_type = dataset.get("dataSourceId", "")
            points = dataset.get("point", [])
            
            if "step_count" in data_type:
                for point in points:
                    val = extract_value(point, "intVal")
                    if val:
                        daily[day]["steps"] += val
            
            elif "active_minutes" in data_type:
                for point in points:
                    val = extract_value(point, "intVal")
                    if val:
                        daily[day]["active_minutes"] += val
            
            elif "calories" in data_type:
                for point in points:
                    val = extract_value(point, "fpVal")
                    if val:
                        daily[day]["calories"] += val
    
    try:
        for day, sleep_hours in get_sleep_hours_by_day(access_token, start, end).items():
            if day not in daily:
                daily[day] = {"steps": 0, "sleep_hours": 0, "active_minutes": 0, "calories": 0}
            daily[day]["sleep_hours"] = sleep_hours
    except Exception as e:
        sleep_error = str(e)
    else:
        sleep_error = None

    # Calculate averages
    days = len(daily)
    if days == 0:
        return None
    
    avg_steps = sum(d["steps"] for d in daily.values()) / days
    avg_sleep = sum(d["sleep_hours"] for d in daily.values() if d["sleep_hours"]) / max(1, sum(1 for d in daily.values() if d["sleep_hours"]))
    avg_active = sum(d["active_minutes"] for d in daily.values()) / days
    avg_calories = sum(d["calories"] for d in daily.values()) / days
    
    return {
        "days": days,
        "avg_steps": round(avg_steps),
        "avg_sleep": round(avg_sleep, 1),
        "avg_active_minutes": round(avg_active),
        "avg_calories": round(avg_calories),
        "daily_breakdown": daily,
        "sleep_error": sleep_error,
    }

def format_weekly_summary(summary):
    """Format weekly summary."""
    if not summary:
        return "No weekly data available yet."
    
    lines = [
        f"📈 **7-Day Fitness Trends**",
        "",
        f"👟 Avg Steps: {summary['avg_steps']:,}/day",
        f"😴 Avg Sleep: {summary['avg_sleep']}h/night",
        f"🔥 Avg Active: {summary['avg_active_minutes']} min/day",
        f"🔥 Avg Calories: {summary['avg_calories']} kcal/day",
        "",
        "**Daily Breakdown:**",
    ]
    
    for day, data in sorted(summary["daily_breakdown"].items()):
        lines.append(f"  {day}: {data['steps']:,} steps, {data['sleep_hours']}h sleep, {data['active_minutes']}m active")

    if summary.get("sleep_error"):
        lines.append("")
        lines.append(f"Sleep unavailable: {summary['sleep_error']}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "weekly":
        token = get_access_token()
        summary = get_weekly_summary(token)
        print(format_weekly_summary(summary))
    else:
        # Default: yesterday's summary
        token = get_access_token()
        summary = get_daily_summary(token)
        print(format_summary(summary))
