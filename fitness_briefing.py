#!/usr/bin/env python3
"""
Fitness Briefing Generator
Combines Google Fit data with weather and cycling recommendations.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, "/home/openclaw/.openclaw/workspace/scripts")
from fitness_tracker import get_access_token, get_daily_summary, format_summary

def get_weather():
    """Fetch weather from wttr.in"""
    try:
        url = "https://wttr.in/Hermosillo,Sonora,Mexico?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            current = data["current_condition"][0]
            return {
                "temp_c": current["temp_C"],
                "condition": current["weatherDesc"][0]["value"],
                "humidity": current["humidity"],
                "wind_kph": current["windspeedKmph"],
                "feels_like_c": current["FeelsLikeC"],
            }
    except Exception as e:
        return {"error": str(e)}

def generate_fitness_briefing():
    """Generate the morning fitness briefing."""
    now = datetime.utcnow()
    
    # Gather data
    weather = get_weather()
    
    # Build briefing
    lines = [
        f"🏃 **Fitness Briefing — {now.strftime('%A, %B %d')}**",
        "",
    ]
    
    # Weather
    if "error" not in weather:
        lines.append(f"🌤️ **Weather in Hermosillo:**")
        lines.append(f"   {weather['condition']}, {weather['temp_c']}°C (feels like {weather['feels_like_c']}°C)")
        lines.append(f"   Humidity: {weather['humidity']}% | Wind: {weather['wind_kph']} km/h")
        
        # Cycling recommendation
        if int(weather['temp_c']) > 35:
            lines.append(f"   ⚠️ **HOT** — Ride early morning or indoor trainer")
        elif int(weather['temp_c']) < 15:
            layers = "Base layer + windbreaker"
            lines.append(f"   🧥 {layers}")
        elif 18 <= int(weather['temp_c']) <= 28 and int(weather['wind_kph']) < 20:
            lines.append(f"   🚴 **PERFECT cycling weather!**")
        
        lines.append("")
    
    # Fitness data
    try:
        token = get_access_token()
        summary = get_daily_summary(token)
        fitness_text = format_summary(summary)
        lines.append(fitness_text)
    except Exception as e:
        lines.append(f"⚠️ Fitness data unavailable: {e}")
    
    # Footer
    lines.append("")
    lines.append(f"⚡ *Briefing generated at {now.strftime('%H:%M UTC')}*")
    lines.append(f"🤖 *KIMO | Your agent, not your assistant*")
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_fitness_briefing())
