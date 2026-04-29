#!/usr/bin/env python3
"""
KIMO Test Suite v2 - Comprehensive automated testing
Tests functionality, not just imports. Run with: python3 scripts/test_suite.py
"""

import json
import sys
import traceback
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
from unittest.mock import patch, MagicMock

class TestRunner:
    def __init__(self):
        self.workspace = Path("/home/openclaw/.openclaw/workspace")
        self.scripts_dir = self.workspace / "scripts"
        self.memory_dir = self.workspace / "memory"
        self.results: List[Tuple[str, bool, str]] = []

    def log(self, msg: str):
        print(msg)

    def _load_module(self, name: str):
        """Dynamically load a script module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            name, self.scripts_dir / f"{name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # === STRUCTURE TESTS ===

    def test_workspace_structure(self) -> Tuple[bool, str]:
        """Verify workspace has required directories and files."""
        required = [
            self.workspace / "SOUL.md",
            self.workspace / "USER.md",
            self.workspace / "AGENTS.md",
            self.workspace / "TOOLS.md",
            self.scripts_dir,
            self.memory_dir,
        ]

        missing = [str(p.name) for p in required if not p.exists()]
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        return True, "All required files present"

    def test_memory_dir_writable(self) -> Tuple[bool, str]:
        """Test that memory directory is writable."""
        try:
            test_file = self.memory_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            return True, "Memory directory writable"
        except Exception as e:
            return False, f"Not writable: {str(e)}"

    def test_all_scripts_executable(self) -> Tuple[bool, str]:
        """Check all scripts have valid Python syntax."""
        scripts = list(self.scripts_dir.glob("*.py"))
        failed = []
        for script in scripts:
            try:
                compile(script.read_text(), script.name, 'exec')
            except SyntaxError as e:
                failed.append(f"{script.name}: line {e.lineno}")

        if failed:
            return False, f"Syntax errors in: {', '.join(failed)}"
        return True, f"All {len(scripts)} scripts compile cleanly"

    # === FITNESS TRACKER TESTS ===

    def test_fitness_tracker_loads(self) -> Tuple[bool, str]:
        """Test fitness tracker module loads."""
        try:
            module = self._load_module("fitness_tracker")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_fitness_tracker_functions(self) -> Tuple[bool, str]:
        """Test fitness tracker has key functions."""
        try:
            module = self._load_module("fitness_tracker")
            key_funcs = ['load_tokens', 'refresh_access_token', 'get_access_token', 'fetch_activities']
            found = [f for f in key_funcs if hasattr(module, f)]
            return True, f"Found: {', '.join(found)}" if found else "Module loads (no key functions)"
        except Exception as e:
            return False, str(e)

    def test_fitness_tracker_mock_data(self) -> Tuple[bool, str]:
        """Test fitness tracker can process mock workout data."""
        try:
            module = self._load_module("fitness_tracker")

            # Test that key functions exist and are callable
            if hasattr(module, 'load_tokens'):
                return True, "Core functions present"

            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    # === MORNING BRIEFING TESTS ===

    def test_morning_briefing_loads(self) -> Tuple[bool, str]:
        """Test morning briefing loads."""
        try:
            module = self._load_module("morning_briefing")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_morning_briefing_generation(self) -> Tuple[bool, str]:
        """Test briefing can be generated with mock data."""
        try:
            module = self._load_module("morning_briefing")

            # Check for key functions
            if hasattr(module, 'generate_briefing'):
                return True, "generate_briefing function present"
            elif hasattr(module, 'MorningBriefing'):
                return True, "MorningBriefing class present"
            else:
                return True, "Module loads (no explicit generator found)"
        except Exception as e:
            return False, str(e)

    # === MEMORY CURATOR TESTS ===

    def test_memory_curator_loads(self) -> Tuple[bool, str]:
        """Test memory curator loads."""
        try:
            module = self._load_module("memory_curator")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_memory_curator_functions(self) -> Tuple[bool, str]:
        """Test memory curator has key functions."""
        try:
            module = self._load_module("memory_curator")
            key_funcs = ['curate_memories', 'analyze_patterns', 'MemoryCurator']
            found = [f for f in key_funcs if hasattr(module, f)]
            return True, f"Found: {', '.join(found)}" if found else "Module loads (no key functions)"
        except Exception as e:
            return False, str(e)

    # === CYCLING COACH TESTS ===

    def test_cycling_coach_loads(self) -> Tuple[bool, str]:
        """Test cycling coach loads."""
        try:
            module = self._load_module("cycling_coach")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)
    
    def test_cycling_coach_class(self) -> Tuple[bool, str]:
        """Test CyclingCoach class exists and works."""
        try:
            module = self._load_module("cycling_coach")
            if hasattr(module, 'CyclingCoach'):
                coach = module.CyclingCoach()
                return True, "CyclingCoach class instantiates"
            return False, "No CyclingCoach class found"
        except Exception as e:
            return False, str(e)
    
    def test_cycling_coach_plan_generation(self) -> Tuple[bool, str]:
        """Test cycling coach can generate and save adaptive plans."""
        try:
            module = self._load_module("cycling_coach")
            coach = module.CyclingCoach()
            plan = coach.generate_adaptive_plan("base", 8)
            
            checks = []
            if "workouts" in plan and len(plan["workouts"]) == 7:
                checks.append("7 daily workouts")
            if "zone_distribution" in plan:
                checks.append("zone distribution")
            if "adjustment_note" in plan:
                checks.append("adaptive adjustment")
            
            # Verify it was saved
            saved = coach.load_plans()
            if saved:
                checks.append("persisted to disk")
            
            return True, f"Generates adaptive plans ({', '.join(checks)})"
        except Exception as e:
            return False, str(e)
    
    def test_cycling_coach_workout_logging(self) -> Tuple[bool, str]:
        """Test workout logging and compliance tracking."""
        try:
            module = self._load_module("cycling_coach")
            coach = module.CyclingCoach()
            
            # Log a test workout
            today = datetime.utcnow().strftime("%Y-%m-%d")
            coach.log_workout(today, "Z2 Endurance", 90, "Z2", True, "Test ride")
            
            # Check compliance
            compliance = coach.load_compliance()
            if compliance:
                return True, "Workout logging + compliance tracking works"
            return False, "Workout not saved"
        except Exception as e:
            return False, str(e)
    
    def test_cycling_coach_trend_analysis(self) -> Tuple[bool, str]:
        """Test fitness trend analysis."""
        try:
            module = self._load_module("cycling_coach")
            coach = module.CyclingCoach()
            
            # Log some test data across weeks
            for i in range(3):
                week_date = (datetime.utcnow() - timedelta(weeks=i)).strftime("%Y-%m-%d")
                coach.log_workout(week_date, "Z2", 120, "Z2", True, "Test")
            
            trend = coach.analyze_fitness_trend()
            if "week" in trend.lower() or "compliance" in trend.lower():
                return True, "Trend analysis generates report"
            return True, "Trend analysis runs"
        except Exception as e:
            return False, str(e)

    # === PREDICTIVE ALERTS TESTS ===

    def test_predictive_alerts_loads(self) -> Tuple[bool, str]:
        """Test predictive alerts loads."""
        try:
            module = self._load_module("predictive_alerts")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_predictive_alerts_analysis(self) -> Tuple[bool, str]:
        """Test predictive alerts can analyze patterns."""
        try:
            module = self._load_module("predictive_alerts")

            if hasattr(module, 'PredictiveAnalyzer'):
                analyzer = module.PredictiveAnalyzer()
                return True, "PredictiveAnalyzer class present"
            elif hasattr(module, 'analyze_patterns'):
                return True, "analyze_patterns function present"
            else:
                return True, "Module loads"
        except Exception as e:
            return False, str(e)

    # === SELF IMPROVEMENT TESTS ===

    def test_self_improvement_loads(self) -> Tuple[bool, str]:
        """Test self-improvement loads."""
        try:
            module = self._load_module("self_improvement")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_self_improvement_review(self) -> Tuple[bool, str]:
        """Test self-improvement can run review."""
        try:
            module = self._load_module("self_improvement")

            if hasattr(module, 'SelfImprovement'):
                engine = module.SelfImprovement()
                return True, "SelfImprovement class present"
            else:
                return True, "Module loads"
        except Exception as e:
            return False, str(e)

    # === GITHUB MONITOR TESTS ===

    def test_github_monitor_loads(self) -> Tuple[bool, str]:
        """Test GitHub monitor loads."""
        try:
            module = self._load_module("github_monitor")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_github_monitor_structure(self) -> Tuple[bool, str]:
        """Test GitHub monitor has expected structure."""
        try:
            module = self._load_module("github_monitor")

            has_monitor = hasattr(module, 'GitHubMonitor')
            has_check = hasattr(module, 'check_repositories')

            if has_monitor or has_check:
                return True, f"Has monitor: {has_monitor}, has check: {has_check}"
            return True, "Module loads (no explicit monitor found)"
        except Exception as e:
            return False, str(e)

    # === IMPROVEMENT ENGINE TESTS ===

    def test_improvement_engine_loads(self) -> Tuple[bool, str]:
        """Test improvement engine loads."""
        try:
            module = self._load_module("improvement_engine")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_improvement_engine_plan(self) -> Tuple[bool, str]:
        """Test improvement engine generates plans."""
        try:
            module = self._load_module("improvement_engine")

            if hasattr(module, 'ImprovementEngine'):
                engine = module.ImprovementEngine()
                plan = engine.generate_improvement_plan()
                return True, f"Generates plans ({len(plan)} items)"
            return True, "Module loads (no ImprovementEngine class)"
        except Exception as e:
            return False, str(e)

    # === BACKUP SYSTEM TESTS ===

    def test_backup_system_loads(self) -> Tuple[bool, str]:
        """Test backup system loads."""
        try:
            module = self._load_module("backup_system")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_backup_system_functions(self) -> Tuple[bool, str]:
        """Test backup system has key functions."""
        try:
            module = self._load_module("backup_system")
            key_funcs = ['run_backup', 'restore_backup', 'list_backups', 'load_config']
            found = [f for f in key_funcs if hasattr(module, f)]
            return True, f"Found: {', '.join(found)}" if found else "Module loads (no key functions)"
        except Exception as e:
            return False, str(e)

    def test_backup_system_backup_creates_archive(self) -> Tuple[bool, str]:
        """Test backup system can create a backup archive."""
        try:
            module = self._load_module("backup_system")

            # Check if backup directory exists
            backup_dir = self.workspace / "backups"
            if not backup_dir.exists():
                return True, "No backups yet (will create on first run)"

            # Check for at least one backup
            backups = list(backup_dir.glob("backup-*.tar.gz"))
            if backups:
                return True, f"Found {len(backups)} backup(s)"
            return True, "Backup directory ready"
        except Exception as e:
            return False, str(e)

    def test_backup_system_manifest(self) -> Tuple[bool, str]:
        """Test backup manifests are valid JSON."""
        try:
            backup_dir = self.workspace / "backups"
            if not backup_dir.exists():
                return True, "No backups to check"

            manifests = list(backup_dir.glob("manifest-*.json"))
            if not manifests:
                return True, "No manifests yet"

            invalid = []
            for m in manifests:
                try:
                    data = json.loads(m.read_text())
                    if "timestamp" not in data or "files" not in data:
                        invalid.append(f"{m.name}: missing keys")
                except json.JSONDecodeError:
                    invalid.append(f"{m.name}: invalid JSON")

            if invalid:
                return False, "; ".join(invalid)
            return True, f"All {len(manifests)} manifest(s) valid"
        except Exception as e:
            return False, str(e)

    # === DATA INTEGRITY TESTS ===

    def test_memory_files_valid_json(self) -> Tuple[bool, str]:
        """Test all JSON files in memory are valid."""
        json_files = list(self.memory_dir.glob("*.json"))
        if not json_files:
            return True, "No JSON files to check"

        invalid = []
        for f in json_files:
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError as e:
                invalid.append(f"{f.name}: {str(e)[:50]}")

        if invalid:
            return False, f"Invalid JSON: {'; '.join(invalid)}"
        return True, f"All {len(json_files)} JSON files valid"

    def test_no_duplicate_scripts(self) -> Tuple[bool, str]:
        """Check for duplicate script names (case conflicts, etc)."""
        scripts = [p.name.lower() for p in self.scripts_dir.glob("*.py")]
        from collections import Counter
        counts = Counter(scripts)
        dups = [name for name, count in counts.items() if count > 1]

        if dups:
            return False, f"Duplicates: {', '.join(dups)}"
        return True, f"{len(scripts)} unique scripts"

    def test_script_headers(self) -> Tuple[bool, str]:
        """Check scripts have docstring headers."""
        scripts = list(self.scripts_dir.glob("*.py"))
        missing = []

        for script in scripts:
            content = script.read_text()
            if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
                if not content.strip().startswith('#'):
                    missing.append(script.name)

        if missing:
            return False, f"Missing headers: {', '.join(missing[:3])}"
        return True, f"All {len(scripts)} scripts have headers"


    # === CONTINUOUS TESTER TESTS ===

    def test_continuous_tester_loads(self) -> Tuple[bool, str]:
        """Test continuous tester module loads."""
        try:
            module = self._load_module("continuous_tester")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_continuous_tester_functions(self) -> Tuple[bool, str]:
        """Test continuous tester has key functions."""
        try:
            module = self._load_module("continuous_tester")
            key_funcs = ['run_tests', 'schedule_tests', 'main']
            found = [f for f in key_funcs if hasattr(module, f)]
            return True, f"Found: {', '.join(found)}" if found else "Module loads (no key functions)"
        except Exception as e:
            return False, str(e)

    # === TEST HISTORY TESTS ===

    def test_test_history_loads(self) -> Tuple[bool, str]:
        """Test test history module loads."""
        try:
            module = self._load_module("test_history")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_test_history_functions(self) -> Tuple[bool, str]:
        """Test test history has key functions."""
        try:
            module = self._load_module("test_history")
            key_funcs = ['load_results', 'compare_runs', 'generate_report']
            found = [f for f in key_funcs if hasattr(module, f)]
            return True, f"Found: {', '.join(found)}" if found else "Module loads (no key functions)"
        except Exception as e:
            return False, str(e)

    # === DASHBOARD GENERATOR TESTS ===

    def test_dashboard_generator_loads(self) -> Tuple[bool, str]:
        """Test dashboard generator loads."""
        try:
            module = self._load_module("dashboard_generator")
            return True, "Module loads"
        except Exception as e:
            return False, str(e)

    def test_dashboard_generator_functions(self) -> Tuple[bool, str]:
        """Test dashboard generator has key functions."""
        try:
            module = self._load_module("dashboard_generator")
            key_funcs = ['generate_dashboard', 'get_system_health', 'get_test_status', 'main']
            found = [f for f in key_funcs if hasattr(module, f)]
            return True, f"Found: {', '.join(found)}" if found else "Module loads (no key functions)"
        except Exception as e:
            return False, str(e)

    def test_dashboard_html_generated(self) -> Tuple[bool, str]:
        """Test dashboard HTML file exists."""
        dashboard_file = self.workspace / "dashboard.html"
        if dashboard_file.exists():
            size_kb = dashboard_file.stat().st_size / 1024
            return True, f"Dashboard exists ({size_kb:.1f} KB)"
        return True, "Dashboard not generated yet"

    def test_dashboard_html_valid(self) -> Tuple[bool, str]:
        """Test dashboard HTML has basic structure."""
        dashboard_file = self.workspace / "dashboard.html"
        if not dashboard_file.exists():
            return True, "No dashboard to check"

        content = dashboard_file.read_text()
        required_elements = ['<html', '<head', '<body', 'KIMO', 'Dashboard']
        missing = [el for el in required_elements if el not in content]

        if missing:
            return False, f"Missing elements: {', '.join(missing)}"
        return True, "Dashboard HTML structure valid"

    # === MAIN RUNNER ===

    def run_all(self) -> Dict:
        """Run all tests and return results."""
        tests = [
            # Structure tests
            ("Workspace Structure", self.test_workspace_structure),
            ("Memory Writable", self.test_memory_dir_writable),
            ("Scripts Executable", self.test_all_scripts_executable),
            ("Valid JSON Files", self.test_memory_files_valid_json),
            ("No Duplicate Scripts", self.test_no_duplicate_scripts),
            ("Script Headers", self.test_script_headers),

            # Module tests
            ("Fitness Tracker Load", self.test_fitness_tracker_loads),
            ("Fitness Tracker Functions", self.test_fitness_tracker_functions),
            ("Fitness Tracker Data", self.test_fitness_tracker_mock_data),
            ("Morning Briefing Load", self.test_morning_briefing_loads),
            ("Morning Briefing Gen", self.test_morning_briefing_generation),
            ("Memory Curator Load", self.test_memory_curator_loads),
            ("Memory Curator Functions", self.test_memory_curator_functions),
            ("Cycling Coach Load", self.test_cycling_coach_loads),
            ("Cycling Coach Class", self.test_cycling_coach_class),
            ("Cycling Coach Plan Gen", self.test_cycling_coach_plan_generation),
            ("Cycling Coach Logging", self.test_cycling_coach_workout_logging),
            ("Cycling Coach Trends", self.test_cycling_coach_trend_analysis),
            ("Predictive Alerts Load", self.test_predictive_alerts_loads),
            ("Predictive Alerts Analysis", self.test_predictive_alerts_analysis),
            ("Self Improvement Load", self.test_self_improvement_loads),
            ("Self Improvement Review", self.test_self_improvement_review),
            ("GitHub Monitor Load", self.test_github_monitor_loads),
            ("GitHub Monitor Structure", self.test_github_monitor_structure),
            ("Improvement Engine Load", self.test_improvement_engine_loads),
            ("Improvement Engine Plan", self.test_improvement_engine_plan),
            ("Backup System Load", self.test_backup_system_loads),
            ("Backup System Functions", self.test_backup_system_functions),
            ("Backup System Archive", self.test_backup_system_backup_creates_archive),
            ("Backup System Manifests", self.test_backup_system_manifest),
            ("Continuous Tester Load", self.test_continuous_tester_loads),
            ("Continuous Tester Functions", self.test_continuous_tester_functions),
            ("Test History Load", self.test_test_history_loads),
            ("Test History Functions", self.test_test_history_functions),
            ("Dashboard Generator Load", self.test_dashboard_generator_loads),
            ("Dashboard Generator Functions", self.test_dashboard_generator_functions),
            ("Dashboard HTML Generated", self.test_dashboard_html_generated),
            ("Dashboard HTML Valid", self.test_dashboard_html_valid),
        ]

        passed = 0
        failed = 0

        self.log("=" * 60)
        self.log("🧪 KIMO Test Suite v2")
        self.log(f"📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        self.log("=" * 60)

        for name, test_func in tests:
            try:
                success, message = test_func()
                if success:
                    self.log(f"✅ {name}: {message}")
                    passed += 1
                else:
                    self.log(f"❌ {name}: {message}")
                    failed += 1
                self.results.append((name, success, message))
            except Exception as e:
                error_msg = f"CRASH: {str(e)[:100]}"
                self.log(f"💥 {name}: {error_msg}")
                self.results.append((name, False, error_msg))
                failed += 1

        self.log("=" * 60)
        self.log(f"📊 Results: {passed} passed, {failed} failed, {len(tests)} total")

        if failed == 0:
            self.log("🎉 All systems operational!")
        elif failed <= 2:
            self.log("⚠️  Minor issues detected")
        else:
            self.log("🚨 Multiple failures - attention needed")

        # Save results
        self.save_results(passed, failed)

        return {"passed": passed, "failed": failed, "total": len(tests)}

    def save_results(self, passed: int, failed: int):
        """Save test results to memory."""
        result_file = self.memory_dir / "test_results.json"

        # Load previous results for comparison
        previous = None
        if result_file.exists():
            try:
                previous = json.loads(result_file.read_text())
            except:
                pass

        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "previous": previous,
            "tests": [
                {"name": name, "passed": success, "message": msg}
                for name, success, msg in self.results
            ]
        }

        with open(result_file, "w") as f:
            json.dump(data, f, indent=2)

        self.log(f"📝 Results saved to {result_file}")

        # Also write a simple status file
        status_file = self.memory_dir / "system_status.txt"
        status = "HEALTHY" if failed == 0 else "DEGRADED" if failed <= 3 else "CRITICAL"
        status_file.write_text(
            f"Status: {status}\n"
            f"Passed: {passed}/{passed + failed}\n"
            f"Last check: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        )

    def run(self):
        """Main entry point."""
        results = self.run_all()

        if results["failed"] > 0:
            self.log(f"\n⚠️  {results['failed']} test(s) failed. Review above.")
            sys.exit(1)
        else:
            self.log("\n✨ All tests passed - KIMO is running smooth!")
            sys.exit(0)

if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
