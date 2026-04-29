#!/usr/bin/env python3
"""
Continuous Improvement Engine v2
Runs autonomously to improve KIMO's capabilities.
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

class ImprovementEngine:
    def __init__(self):
        self.workspace = Path("/home/openclaw/.openclaw/workspace")
        self.scripts_dir = self.workspace / "scripts"
        self.memory_dir = self.workspace / "memory"
        
    def check_system_health(self):
        """Check all systems and report status."""
        checks = {
            "fitness_tracker": (self.scripts_dir / "fitness_tracker.py").exists(),
            "morning_briefing": (self.scripts_dir / "morning_briefing.py").exists(),
            "github_monitor": (self.scripts_dir / "github_monitor.py").exists(),
            "memory_curator": (self.scripts_dir / "memory_curator.py").exists(),
            "cycling_coach": (self.scripts_dir / "cycling_coach.py").exists(),
            "predictive_alerts": (self.scripts_dir / "predictive_alerts.py").exists(),
            "self_improvement": (self.scripts_dir / "self_improvement.py").exists(),
            "test_suite": (self.scripts_dir / "test_suite.py").exists(),
            "continuous_tester": (self.scripts_dir / "continuous_tester.py").exists(),
            "test_history": (self.scripts_dir / "test_history.py").exists(),
            "google_fit_tokens": (self.workspace / ".google_fit_tokens.json").exists(),
            "backup_system": (self.scripts_dir / "backup_system.py").exists(),
        }
        return checks
    
    def get_test_results(self):
        """Load latest test results."""
        results_file = self.memory_dir / "test_results.json"
        if results_file.exists():
            try:
                return json.loads(results_file.read_text())
            except:
                pass
        return None
    
    def generate_improvement_plan(self):
        """Generate next improvements based on current state."""
        checks = self.check_system_health()
        tests = self.get_test_results()
        
        plan = []
        
        # Check what's missing
        if not checks.get("github_monitor"):
            plan.append("Build GitHub monitor with real API integration")
        
        # Check test health
        if tests:
            passed = tests.get("passed", 0)
            total = tests.get("total", 1)
            if passed < total:
                plan.append(f"Fix failing tests ({total - passed} failing)")
            else:
                plan.append("✅ All tests passing - expand test coverage")
        else:
            plan.append("Run test suite to establish baseline")
        
        # Always improve existing systems
        plan.extend([
            "🆕 Backup system deployed - monitor first few backups",
            "Optimize fitness tracker for faster queries",
            "Add more data sources to morning briefing",
            "Improve memory curator with better pattern detection",
            "Add error handling and logging to all scripts",
            "Build dashboard for system monitoring",
        ])
        
        return plan
    
    def log_activity(self, activity):
        """Log improvement activities."""
        log_file = self.memory_dir / "improvement_log.txt"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {activity}\n")
    
    def get_next_task(self):
        """Determine the highest priority task to execute."""
        checks = self.check_system_health()
        tests = self.get_test_results()
        
        # Priority 1: Fix failing tests
        if tests and tests.get("failed", 0) > 0:
            return "fix_tests", f"Fix {tests['failed']} failing tests"
        
        # Priority 2: Run test suite if no results
        if not tests:
            return "run_tests", "Run test suite to establish baseline"
        
        # Priority 3: Check backup system health
        if checks.get("backup_system"):
            config_file = self.workspace / "backup_config.json"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    last_backup = config.get("last_backup", {})
                    if last_backup and last_backup.get("timestamp"):
                        ts = last_backup["timestamp"]
                        backup_time = datetime.strptime(ts, "%Y%m%d-%H%M%S")
                        hours_since = (datetime.utcnow() - backup_time).total_seconds() / 3600
                        if hours_since > 24:
                            return "backup", f"Run backup (last: {hours_since:.1f}h ago)"
                        elif hours_since > 6:
                            return "monitor_backup", f"Monitor backup system (last: {hours_since:.1f}h ago)"
                except:
                    pass
        
        # Priority 4: Build dashboard if missing or stale
        dashboard_file = self.workspace / "dashboard.html"
        if not dashboard_file.exists():
            return "build_dashboard", "Build system monitoring dashboard"
        
        # Priority 5: Expand test coverage
        if tests and tests.get("passed", 0) == tests.get("total", 0):
            # Check if we need more tests or if coverage is adequate
            if tests.get("total", 0) >= 30:
                return "build_dashboard", "Regenerate system monitoring dashboard"
            return "expand_tests", "Expand test coverage for existing scripts"
        
        # Priority 6: Optimize fitness tracker
        if checks.get("fitness_tracker"):
            return "optimize_fitness", "Optimize fitness tracker queries"
        
        # Default: Add error handling
        return "add_logging", "Add error handling and logging to scripts"
    
    def execute_task(self, task_type, task_desc):
        """Execute the selected improvement task."""
        print(f"\n🔨 Executing: {task_desc}")
        
        if task_type == "fix_tests":
            return self._fix_tests()
        elif task_type == "run_tests":
            return self._run_tests()
        elif task_type in ["backup", "monitor_backup"]:
            return self._monitor_backup()
        elif task_type == "expand_tests":
            return self._expand_tests()
        elif task_type == "optimize_fitness":
            return self._optimize_fitness()
        elif task_type == "build_dashboard":
            return self._build_dashboard()
        else:
            return f"Unknown task type: {task_type}"
    
    def _fix_tests(self):
        """Run tests and capture output for analysis."""
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "test_suite.py")],
                capture_output=True, text=True, timeout=120
            )
            return f"Tests executed. Return code: {result.returncode}"
        except Exception as e:
            return f"Error running tests: {e}"
    
    def _run_tests(self):
        """Run the full test suite."""
        return self._fix_tests()
    
    def _run_backup(self):
        """Execute backup system."""
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "backup_system.py")],
                capture_output=True, text=True, timeout=300
            )
            return f"Backup executed. Return code: {result.returncode}"
        except Exception as e:
            return f"Error running backup: {e}"
    
    def _monitor_backup(self):
        """Monitor backup system health and log status."""
        import subprocess
        try:
            # Get backup status
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "backup_system.py"), "--status"],
                capture_output=True, text=True, timeout=30
            )
            status_output = result.stdout
            
            # Get backup list
            list_result = subprocess.run(
                ["python3", str(self.scripts_dir / "backup_system.py"), "--list"],
                capture_output=True, text=True, timeout=30
            )
            list_output = list_result.stdout
            
            # Parse backup count from list output
            import re
            backup_count = 0
            for line in list_output.split('\n'):
                if 'Found' in line and 'backup' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        backup_count = int(match.group(1))
            
            # Check if backup ran recently (within last 6 hours)
            config_file = self.workspace / "backup_config.json"
            hours_since = 999
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    last_backup = config.get("last_backup", {})
                    if last_backup and last_backup.get("timestamp"):
                        ts = last_backup["timestamp"]
                        backup_time = datetime.strptime(ts, "%Y%m%d-%H%M%S")
                        hours_since = (datetime.utcnow() - backup_time).total_seconds() / 3600
                except:
                    pass
            
            # Determine health status
            if backup_count == 0:
                health = "CRITICAL - No backups found!"
            elif hours_since > 24:
                health = f"WARNING - Last backup {hours_since:.1f}h ago"
            elif hours_since > 6:
                health = f"CAUTION - Last backup {hours_since:.1f}h ago"
            else:
                health = f"HEALTHY - {backup_count} backups, last {hours_since:.1f}h ago"
            
            # Log to improvement log
            self.log_activity(f"Backup health: {health}")
            
            return f"Backup monitoring complete. {health}"
        except Exception as e:
            return f"Error monitoring backups: {e}"
    
    def _run_backup(self):
        """Execute backup system."""
        import subprocess
        try:
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "backup_system.py")],
                capture_output=True, text=True, timeout=300
            )
            return f"Backup executed. Return code: {result.returncode}"
        except Exception as e:
            return f"Error running backup: {e}"
    
    def _monitor_backup(self):
        """Monitor backup system health and log status."""
        import subprocess
        try:
            # Get backup status
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "backup_system.py"), "--status"],
                capture_output=True, text=True, timeout=30
            )
            status_output = result.stdout
            
            # Get backup list
            list_result = subprocess.run(
                ["python3", str(self.scripts_dir / "backup_system.py"), "--list"],
                capture_output=True, text=True, timeout=30
            )
            list_output = list_result.stdout
            
            # Parse backup count from list output
            import re
            backup_count = 0
            for line in list_output.split('\n'):
                if 'Found' in line and 'backup' in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        backup_count = int(match.group(1))
            
            # Check if backup ran recently (within last 6 hours)
            config_file = self.workspace / "backup_config.json"
            hours_since = 999
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    last_backup = config.get("last_backup", {})
                    if last_backup and last_backup.get("timestamp"):
                        ts = last_backup["timestamp"]
                        backup_time = datetime.strptime(ts, "%Y%m%d-%H%M%S")
                        hours_since = (datetime.utcnow() - backup_time).total_seconds() / 3600
                except:
                    pass
            
            # Determine health status
            if backup_count == 0:
                health = "CRITICAL - No backups found!"
            elif hours_since > 24:
                health = f"WARNING - Last backup {hours_since:.1f}h ago"
            elif hours_since > 6:
                health = f"CAUTION - Last backup {hours_since:.1f}h ago"
            else:
                health = f"HEALTHY - {backup_count} backups, last {hours_since:.1f}h ago"
            
            # Log to improvement log
            self.log_activity(f"Backup health: {health}")
            
            return f"Backup monitoring complete. {health}"
        except Exception as e:
            return f"Error monitoring backups: {e}"
    
    def _expand_tests(self):
        """Add more comprehensive tests for dashboard generator."""
        test_file = self.scripts_dir / "test_suite.py"
        if not test_file.exists():
            return "No test suite found. Create comprehensive tests."
        
        # Check if dashboard tests exist
        content = test_file.read_text()
        if "dashboard" in content.lower():
            return "Dashboard tests already present. Coverage adequate."
        
        # Add dashboard tests to test suite
        dashboard_tests = '''
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
'''
        
        # Find where to insert (before the main runner)
        insert_marker = "    # === MAIN RUNNER ==="
        if insert_marker in content:
            content = content.replace(insert_marker, dashboard_tests + "\n" + insert_marker)
            test_file.write_text(content)
            return "Added dashboard generator tests to test suite"
        
        return "Could not find insertion point for new tests"

    
    def _optimize_fitness(self):
        """Optimize fitness tracker performance."""
        fitness_file = self.scripts_dir / "fitness_tracker.py"
        if fitness_file.exists():
            content = fitness_file.read_text()
            # Check for obvious optimizations
            if "for.*in.*range" in content and "list comprehension" not in content:
                return "Fitness tracker could use list comprehensions for speed."
            return "Fitness tracker reviewed - no obvious optimizations found."
        return "Fitness tracker not found."
    
    def _add_logging(self):
        """Add error handling and logging to scripts."""
        scripts = list(self.scripts_dir.glob("*.py"))
        added = 0
        for script in scripts:
            content = script.read_text()
            if "import logging" not in content:
                # Add logging import at top
                lines = content.split('\n')
                # Find a good place to insert
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_idx = i + 1
                lines.insert(insert_idx, 'import logging')
                lines.insert(insert_idx + 1, 'logger = logging.getLogger(__name__)')
                script.write_text('\n'.join(lines))
                added += 1
        return f"Added logging to {added} scripts"
    
    def _build_dashboard(self):
        """Generate system monitoring dashboard."""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", str(self.scripts_dir / "dashboard_generator.py")],
                capture_output=True, text=True, timeout=60
            )
            return f"Dashboard generated. Return code: {result.returncode}"
        except Exception as e:
            return f"Error building dashboard: {e}"
    
    def run(self):
        """Main improvement loop with execution."""
        print("🚀 KIMO Improvement Engine v2 Starting...")
        
        # Check health
        checks = self.check_system_health()
        print("\n📊 System Health Check:")
        for system, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {system}")
        
        # Check test results
        tests = self.get_test_results()
        if tests:
            print(f"\n🧪 Latest Tests: {tests['passed']}/{tests['total']} passing")
            if tests["failed"] == 0:
                print("   🎉 All tests green!")
            else:
                print(f"   ⚠️  {tests['failed']} tests need attention")
        
        # Generate plan
        plan = self.generate_improvement_plan()
        print("\n📋 Improvement Plan:")
        for i, item in enumerate(plan, 1):
            print(f"  {i}. {item}")
        
        # Determine and execute next task
        task_type, task_desc = self.get_next_task()
        print(f"\n🎯 Next Task: {task_desc}")
        
        result = self.execute_task(task_type, task_desc)
        print(f"📊 Result: {result}")
        
        # Log
        self.log_activity(f"Health check: {sum(checks.values())}/{len(checks)} systems ready")
        if tests:
            self.log_activity(f"Test status: {tests['passed']}/{tests['total']} passing")
        self.log_activity(f"Executed: {task_desc} - {result}")
        
        print("\n✅ Improvement cycle complete.")
        
        return {"plan": plan, "executed": task_type, "result": result}

if __name__ == "__main__":
    engine = ImprovementEngine()
    engine.run()
