#!/usr/bin/env python3
"""
Cycling Coach v2 - Adaptive Training System
Periodized plans that learn from your actual training data.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Training zones (based on HR or power)
ZONES = {
    "Z1": {"name": "Recovery", "hr": "< 68% max", "feel": "Easy conversation", "color": "#4ade80"},
    "Z2": {"name": "Endurance", "hr": "68-82% max", "feel": "Steady, controlled breathing", "color": "#60a5fa"},
    "Z3": {"name": "Tempo", "hr": "82-89% max", "feel": "Sustainable hard, deeper breathing", "color": "#fbbf24"},
    "Z4": {"name": "Threshold", "hr": "89-95% max", "feel": "Hard, short sentences only", "color": "#fb923c"},
    "Z5": {"name": "VO2 Max", "hr": "95-100% max", "feel": "Very hard, unsustainable", "color": "#f87171"},
    "Z6": {"name": "Anaerobic", "hr": "N/A", "feel": "Maximum effort, short bursts", "color": "#c084fc"},
}

# Periodization templates
PERIODIZATION = {
    "base": {
        "weeks": 4,
        "focus": "Build aerobic base, increase volume",
        "distribution": {"Z1": 20, "Z2": 60, "Z3": 15, "Z4": 5, "Z5": 0},
        "weekly_hours": "8-12",
    },
    "build": {
        "weeks": 4,
        "focus": "Increase intensity, introduce threshold work",
        "distribution": {"Z1": 15, "Z2": 45, "Z3": 25, "Z4": 12, "Z5": 3},
        "weekly_hours": "10-14",
    },
    "peak": {
        "weeks": 2,
        "focus": "Maximize fitness, reduce volume maintain intensity",
        "distribution": {"Z1": 20, "Z2": 30, "Z3": 30, "Z4": 15, "Z5": 5},
        "weekly_hours": "8-10",
    },
    "recovery": {
        "weeks": 1,
        "focus": "Active recovery, mental break",
        "distribution": {"Z1": 60, "Z2": 30, "Z3": 10, "Z4": 0, "Z5": 0},
        "weekly_hours": "4-6",
    },
}

# Workout templates by phase
WORKOUT_TEMPLATES = {
    "base": [
        ("Mon", "Rest or Z1 spin", 0, "Z1"),
        ("Tue", "Z2 Endurance", 90, "Z2"),
        ("Wed", "Z2 Endurance + drills", 75, "Z2"),
        ("Thu", "Rest", 0, "Z1"),
        ("Fri", "Z2 Long ride", 120, "Z2"),
        ("Sat", "Z3 Tempo blocks", 90, "Z3"),
        ("Sun", "Z2 Recovery spin", 60, "Z2"),
    ],
    "build": [
        ("Mon", "Rest", 0, "Z1"),
        ("Tue", "Z4 Threshold intervals", 75, "Z4"),
        ("Wed", "Z2 Endurance", 90, "Z2"),
        ("Thu", "Z3 Tempo", 75, "Z3"),
        ("Fri", "Rest", 0, "Z1"),
        ("Sat", "Z4/Z5 Intervals", 90, "Z4"),
        ("Sun", "Z2 Long ride", 150, "Z2"),
    ],
    "peak": [
        ("Mon", "Rest", 0, "Z1"),
        ("Tue", "Z5 VO2 Max", 60, "Z5"),
        ("Wed", "Z2 Easy spin", 45, "Z2"),
        ("Thu", "Z4 Threshold", 75, "Z4"),
        ("Fri", "Rest", 0, "Z1"),
        ("Sat", "Z3/Z4 Race simulation", 90, "Z4"),
        ("Sun", "Z1 Recovery", 45, "Z1"),
    ],
    "recovery": [
        ("Mon", "Rest", 0, "Z1"),
        ("Tue", "Z1 Easy spin", 45, "Z1"),
        ("Wed", "Rest", 0, "Z1"),
        ("Thu", "Z2 Coffee ride", 60, "Z2"),
        ("Fri", "Rest", 0, "Z1"),
        ("Sat", "Z1/Z2 Social ride", 90, "Z2"),
        ("Sun", "Rest", 0, "Z1"),
    ],
}

class CyclingCoach:
    """Adaptive cycling coach that tracks plans and adapts to compliance."""
    
    def __init__(self, workspace=None):
        self.workspace = Path(workspace or "/home/openclaw/.openclaw/workspace")
        self.memory_dir = self.workspace / "memory"
        self.plans_file = self.memory_dir / "training_plans.json"
        self.compliance_file = self.memory_dir / "workout_compliance.json"
        self.athlete_file = self.memory_dir / "athlete_profile.json"
        
        self._ensure_dirs()
        self.athlete = self._load_athlete()
    
    def _ensure_dirs(self):
        self.memory_dir.mkdir(exist_ok=True)
    
    def _load_athlete(self):
        if self.athlete_file.exists():
            return json.loads(self.athlete_file.read_text())
        return {
            "age": 30,
            "max_hr": 190,
            "ftp": 250,
            "weight_kg": 75,
            "experience": "intermediate",
            "goal_event": None,
            "goal_date": None,
        }
    
    def save_athlete(self, **kwargs):
        self.athlete.update(kwargs)
        self.athlete_file.write_text(json.dumps(self.athlete, indent=2))
    
    def calculate_max_hr(self):
        return 220 - self.athlete["age"]
    
    def load_plans(self):
        if self.plans_file.exists():
            return json.loads(self.plans_file.read_text())
        return {}
    
    def save_plan(self, plan_id, plan_data):
        plans = self.load_plans()
        plans[plan_id] = plan_data
        self.plans_file.write_text(json.dumps(plans, indent=2))
    
    def load_compliance(self):
        if self.compliance_file.exists():
            return json.loads(self.compliance_file.read_text())
        return {}
    
    def log_workout(self, date, planned, actual_duration, actual_zone, completed=True, notes=""):
        """Log a completed (or missed) workout."""
        compliance = self.load_compliance()
        
        week_key = self._week_key(date)
        if week_key not in compliance:
            compliance[week_key] = []
        
        compliance[week_key].append({
            "date": date,
            "planned": planned,
            "actual_duration": actual_duration,
            "actual_zone": actual_zone,
            "completed": completed,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        self.compliance_file.write_text(json.dumps(compliance, indent=2))
    
    def _week_key(self, date_str=None):
        if date_str is None:
            d = datetime.utcnow()
        else:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        # Week starts Monday
        monday = d - timedelta(days=d.weekday())
        return monday.strftime("%Y-W%U")
    
    def get_weekly_compliance(self, week_key=None):
        """Calculate compliance % for a week."""
        if week_key is None:
            week_key = self._week_key()
        
        compliance = self.load_compliance()
        workouts = compliance.get(week_key, [])
        
        if not workouts:
            return 0.0
        
        completed = sum(1 for w in workouts if w["completed"])
        return (completed / len(workouts)) * 100
    
    def get_4week_trend(self):
        """Get compliance trend over last 4 weeks."""
        compliance = self.load_compliance()
        
        weeks = []
        now = datetime.utcnow()
        for i in range(4):
            week_date = now - timedelta(weeks=i)
            week_key = self._week_key(week_date.strftime("%Y-%m-%d"))
            pct = self.get_weekly_compliance(week_key)
            weeks.append({"week": week_key, "compliance": pct})
        
        return weeks
    
    def generate_adaptive_plan(self, phase="base", hours=10, start_date=None):
        """Generate a plan that adapts based on recent compliance."""
        if start_date is None:
            start_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Check recent compliance to adjust
        trend = self.get_4week_trend()
        avg_compliance = sum(w["compliance"] for w in trend) / len(trend) if trend else 75
        
        # Adjust hours based on compliance
        adjusted_hours = hours
        if avg_compliance < 60:
            adjusted_hours = max(6, hours - 2)
            adjustment_note = f"Reduced to {adjusted_hours}h (compliance: {avg_compliance:.0f}%)"
        elif avg_compliance > 90:
            adjusted_hours = min(16, hours + 1)
            adjustment_note = f"Increased to {adjusted_hours}h (compliance: {avg_compliance:.0f}%)"
        else:
            adjustment_note = f"Maintained {adjusted_hours}h (compliance: {avg_compliance:.0f}%)"
        
        plan = self._build_plan(phase, adjusted_hours, start_date)
        plan["adjustment_note"] = adjustment_note
        plan["compliance_trend"] = trend
        
        plan_id = f"{phase}-{start_date}"
        self.save_plan(plan_id, plan)
        
        return plan
    
    def _build_plan(self, phase, hours, start_date):
        """Build a weekly plan structure."""
        plan_info = PERIODIZATION.get(phase, PERIODIZATION["base"])
        templates = WORKOUT_TEMPLATES.get(phase, WORKOUT_TEMPLATES["base"])
        
        # Scale workout durations to hit target hours
        total_template_minutes = sum(m for _, _, m, _ in templates if m > 0)
        scale_factor = (hours * 60) / total_template_minutes if total_template_minutes > 0 else 1
        
        workouts = []
        for day, name, minutes, zone in templates:
            scaled = int(minutes * scale_factor) if minutes > 0 else 0
            workouts.append({
                "day": day,
                "name": name,
                "planned_duration": scaled,
                "zone": zone,
                "completed": False,
                "actual_duration": 0,
            })
        
        return {
            "phase": phase,
            "week_start": start_date,
            "target_hours": hours,
            "focus": plan_info["focus"],
            "workouts": workouts,
            "zone_distribution": plan_info["distribution"],
            "created_at": datetime.utcnow().isoformat(),
        }
    
    def format_plan(self, plan):
        """Format plan as readable text."""
        lines = [
            f"🚴 **Adaptive Training Plan — {plan['phase'].upper()} PHASE**",
            f"",
            f"**Week of:** {plan['week_start']}",
            f"**Focus:** {plan['focus']}",
            f"**Target:** {plan['target_hours']}h/week",
        ]
        
        if "adjustment_note" in plan:
            lines.append(f"**Adjustment:** {plan['adjustment_note']}")
        
        lines.append(f"")
        lines.append(f"**Schedule:**")
        
        for w in plan["workouts"]:
            status = "✅" if w["completed"] else "⬜"
            zone_info = ZONES.get(w["zone"], {})
            color = zone_info.get("color", "#fff")
            
            if w["planned_duration"] > 0:
                if w["actual_duration"] > 0:
                    lines.append(f"  {status} **{w['day']}:** {w['name']} ({w['actual_duration']}/{w['planned_duration']}min) [{w['zone']}]")
                else:
                    lines.append(f"  {status} **{w['day']}:** {w['name']} ({w['planned_duration']}min) [{w['zone']}]")
            else:
                lines.append(f"  {status} **{w['day']}:** {w['name']}")
        
        lines.append(f"")
        lines.append(f"**Zone Distribution:**")
        for zone, pct in plan["zone_distribution"].items():
            if pct > 0:
                zone_name = ZONES[zone]["name"]
                lines.append(f"  {zone} ({zone_name}): {pct}%")
        
        if "compliance_trend" in plan:
            lines.append(f"")
            lines.append(f"**4-Week Compliance Trend:**")
            for t in plan["compliance_trend"]:
                bar = "█" * int(t["compliance"] / 10) + "░" * (10 - int(t["compliance"] / 10))
                lines.append(f"  {t['week']}: {bar} {t['compliance']:.0f}%")
        
        lines.append(f"")
        lines.append(f"**Nutrition Timing:**")
        lines.append(f"  • Pre-ride (2h before): Carbs 1-2g/kg")
        lines.append(f"  • During (>90min): 60g carbs/hour")
        lines.append(f"  • Post-ride (within 30min): 60g carbs + 20g protein")
        lines.append(f"  • Hydration: 500ml/hour + electrolytes")
        
        return "\n".join(lines)
    
    def get_current_plan(self):
        """Get the most recent active plan."""
        plans = self.load_plans()
        if not plans:
            return None
        
        # Sort by creation date, newest first
        sorted_plans = sorted(
            plans.items(),
            key=lambda x: x[1].get("created_at", ""),
            reverse=True
        )
        return sorted_plans[0][1] if sorted_plans else None
    
    def analyze_fitness_trend(self):
        """Analyze fitness trends from compliance data."""
        compliance = self.load_compliance()
        
        if not compliance:
            return "No workout data yet. Start logging rides!"
        
        # Calculate weekly stats
        weeks = []
        for week_key, workouts in sorted(compliance.items())[-8:]:  # Last 8 weeks
            total_duration = sum(w["actual_duration"] for w in workouts if w["completed"])
            completed = sum(1 for w in workouts if w["completed"])
            total = len(workouts)
            
            weeks.append({
                "week": week_key,
                "hours": total_duration / 60,
                "compliance": (completed / total * 100) if total > 0 else 0,
                "sessions": completed,
            })
        
        if len(weeks) < 2:
            return f"Only {len(weeks)} week(s) of data. Keep logging!"
        
        # Calculate trends
        recent_hours = weeks[-1]["hours"]
        avg_hours = sum(w["hours"] for w in weeks[:-1]) / len(weeks[:-1])
        hours_trend = recent_hours - avg_hours
        
        recent_compliance = weeks[-1]["compliance"]
        avg_compliance = sum(w["compliance"] for w in weeks[:-1]) / len(weeks[:-1])
        compliance_trend = recent_compliance - avg_compliance
        
        lines = [
            f"📈 **Fitness Trend Analysis (Last {len(weeks)} weeks)**",
            f"",
            f"**Volume Trend:** {hours_trend:+.1f}h vs avg",
            f"**Compliance Trend:** {compliance_trend:+.1f}% vs avg",
            f"",
            f"**Weekly Breakdown:**",
        ]
        
        for w in weeks:
            bar = "█" * int(w["compliance"] / 10) + "░" * (10 - int(w["compliance"] / 10))
            lines.append(f"  {w['week']}: {w['hours']:.1f}h | {bar} {w['compliance']:.0f}% | {w['sessions']} sessions")
        
        lines.append(f"")
        
        # Recommendations
        if hours_trend > 2 and compliance_trend < -10:
            lines.append(f"⚠️ **RISK:** Volume up but compliance dropping. You're overreaching.")
            lines.append(f"   → Reduce volume 15% next week")
            lines.append(f"   → Prioritize sleep (8h+)")
            lines.append(f"   → Add 1 rest day")
        elif hours_trend > 1:
            lines.append(f"✅ **Good:** Volume increasing sustainably")
            lines.append(f"   → Maintain current trajectory")
            lines.append(f"   → Watch for morning HR spikes (fatigue indicator)")
        elif hours_trend < -1.5:
            lines.append(f"⚠️ **Concern:** Volume dropping")
            lines.append(f"   → Check: Life stress? Motivation? Injury?")
            lines.append(f"   → If time-limited: switch to HIIT (2x 30min Z4 sessions/week)")
        else:
            lines.append(f"🟢 **Stable:** Consistent training load")
            lines.append(f"   → Good foundation. Consider adding intensity if goal event approaching")
        
        if compliance_trend > 10:
            lines.append(f"🎯 **Compliance improving!** You're building the habit.")
        elif compliance_trend < -15:
            lines.append(f"🔴 **Compliance dropping.** Review schedule realism or motivation.")
        
        return "\n".join(lines)

# Legacy functions for backward compatibility
def generate_week_plan(phase="base", hours=10, rest_days=2, age=30):
    """Legacy function - generates a simple plan."""
    coach = CyclingCoach()
    coach.save_athlete(age=age)
    plan = coach.generate_adaptive_plan(phase, hours)
    return coach.format_plan(plan)

def race_prep_checklist(race_type="road", days_until=7):
    """Generate race preparation checklist."""
    lines = [
        f"🏁 **Race Prep Checklist — {race_type.upper()} RACE**",
        f"**Race in:** {days_until} days",
        f"",
    ]
    
    if days_until >= 7:
        lines.append(f"**Week Before:**")
        lines.append(f"  ✅ Taper volume to 60% of normal")
        lines.append(f"  ✅ Maintain intensity (short sharp efforts)")
        lines.append(f"  ✅ Check bike: brakes, tires, chain, bolts")
        lines.append(f"  ✅ Plan race nutrition (practice on training rides)")
        lines.append(f"  ✅ Sleep 8h+/night")
        lines.append(f"  ✅ Check weather forecast, plan kit")
        lines.append(f"")
    
    if days_until >= 3:
        lines.append(f"**3 Days Before:**")
        lines.append(f"  ✅ Carb load (8-10g carbs/kg bodyweight)")
        lines.append(f"  ✅ Hydrate aggressively")
        lines.append(f"  ✅ Short easy rides only (30-45min Z1/Z2)")
        lines.append(f"  ✅ Prep race kit, check weather")
        lines.append(f"")
    
    if days_until >= 1:
        lines.append(f"**Day Before:**")
        lines.append(f"  ✅ Easy 20min spin with 2x 30sec openers")
        lines.append(f"  ✅ Pre-race meal: familiar, high carb, low fiber")
        lines.append(f"  ✅ Early bedtime (aim for 9h sleep)")
        lines.append(f"  ✅ Pack: kit, shoes, helmet, nutrition, tools, pump, CO2")
        lines.append(f"")
    
    lines.append(f"**Race Day:**")
    lines.append(f"  ✅ Breakfast 3h before: 2g carbs/kg")
    lines.append(f"  ✅ Arrive early: warm-up 20-30min")
    lines.append(f"  ✅ Pre-race: 1 gel 15min before start")
    lines.append(f"  ✅ During: 60g carbs/hour from hour 1")
    lines.append(f"  ✅ Pacing: start conservative, finish strong")
    lines.append(f"  ✅ Post-race: immediate recovery shake + 30min easy spin")
    
    return "\n".join(lines)

def calculate_max_hr(age=30):
    return 220 - age

if __name__ == "__main__":
    import sys
    
    coach = CyclingCoach()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "plan":
            phase = sys.argv[2] if len(sys.argv) > 2 else "base"
            hours = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            plan = coach.generate_adaptive_plan(phase, hours)
            print(coach.format_plan(plan))
            
        elif command == "race":
            race_type = sys.argv[2] if len(sys.argv) > 2 else "road"
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
            print(race_prep_checklist(race_type, days))
            
        elif command == "zones":
            print("🚴 **Heart Rate Zones**")
            max_hr = int(sys.argv[2]) if len(sys.argv) > 2 else coach.calculate_max_hr()
            for zone, info in ZONES.items():
                print(f"  {zone} ({info['name']}): {info['hr']} | {info['feel']}")
                
        elif command == "log":
            if len(sys.argv) < 4:
                print("Usage: cycling_coach.py log <date> <duration_minutes> [zone] [notes]")
                sys.exit(1)
            date = sys.argv[2]
            duration = int(sys.argv[3])
            zone = sys.argv[4] if len(sys.argv) > 4 else "Z2"
            notes = sys.argv[5] if len(sys.argv) > 5 else ""
            coach.log_workout(date, "Manual entry", duration, zone, True, notes)
            print(f"✅ Logged: {date} - {duration}min {zone} - {notes}")
            
        elif command == "trend":
            print(coach.analyze_fitness_trend())
            
        elif command == "compliance":
            trend = coach.get_4week_trend()
            print("📊 4-Week Compliance:")
            for t in trend:
                bar = "█" * int(t["compliance"] / 10) + "░" * (10 - int(t["compliance"] / 10))
                print(f"  {t['week']}: {bar} {t['compliance']:.0f}%")
                
        elif command == "profile":
            print("👤 Athlete Profile:")
            for k, v in coach.athlete.items():
                print(f"  {k}: {v}")
                
        elif command == "set":
            if len(sys.argv) < 4:
                print("Usage: cycling_coach.py set <field> <value>")
                sys.exit(1)
            field = sys.argv[2]
            value = sys.argv[3]
            # Try to convert to int/float
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            coach.save_athlete(**{field: value})
            print(f"✅ Updated {field} = {value}")
            
        else:
            print("Commands: plan [phase] [hours] | race [type] [days] | zones [max_hr] | log <date> <min> [zone] [notes] | trend | compliance | profile | set <field> <value>")
    else:
        # Default: show current plan or generate base
        current = coach.get_current_plan()
        if current:
            print(coach.format_plan(current))
        else:
            plan = coach.generate_adaptive_plan("base", 10)
            print(coach.format_plan(plan))
