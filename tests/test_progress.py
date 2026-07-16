import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "plugins/vibe-learn/skills/vibe-learn/scripts/progress.py"
FIXTURES = Path(__file__).parent / "fixtures"


class ProgressTests(unittest.TestCase):
    def cli(self, project, *args, check=True):
        return subprocess.run([sys.executable, str(SCRIPT), "--project", str(project), *args], text=True, capture_output=True, check=check)

    def state(self, project):
        return json.loads((project / ".vibe-learn/state.json").read_text())

    def test_init_teach_and_render(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            self.cli(project, "teach", "--concept", "Async Error Propagation", "--stack", "javascript")
            data = self.state(project)
            self.assertEqual(data["schema_version"], 2)
            self.assertIn("async-error-propagation", data["concepts"])
            self.assertTrue((project / ".vibe-learn/progress.md").exists())

    def test_review_schedule_and_cap(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            self.cli(project, "teach", "--concept", "retry logic", "--stack", "python")
            for _ in range(6): self.cli(project, "result", "--concept", "retry-logic", "--outcome", "correct")
            item = self.state(project)["concepts"]["retry-logic"]
            self.assertEqual(item["interval_days"], 14); self.assertFalse(item["shaky"])
            self.cli(project, "result", "--concept", "retry-logic", "--outcome", "partial")
            item = self.state(project)["concepts"]["retry-logic"]
            self.assertEqual(item["interval_days"], 2); self.assertTrue(item["shaky"])

    def test_malformed_state_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); directory = project / ".vibe-learn"; directory.mkdir()
            original = (FIXTURES / "malformed-state.json").read_text(); (directory / "state.json").write_text(original)
            result = self.cli(project, "validate", check=False)
            self.assertNotEqual(result.returncode, 0); self.assertEqual((directory / "state.json").read_text(), original)

    def test_migration_dry_run_then_migrate(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); directory = project / ".vibe-learn"; directory.mkdir()
            (directory / "progress.md").write_text((FIXTURES / "legacy-progress.md").read_text())
            result = json.loads(self.cli(project, "migrate", "--dry-run").stdout)
            self.assertTrue(result["dry_run"]); self.assertFalse((directory / "state.json").exists())
            self.cli(project, "migrate"); data = self.state(project)
            self.assertEqual(data["profile"]["level"], "advanced")
            self.assertTrue(data["concepts"]["fetch-res-ok-vs-throw"]["shaky"])
            self.assertTrue((directory / "progress.v1.2.backup.md").exists())

    def test_mistake_evidence_is_bounded_and_secret_safe(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            result = self.cli(project, "mistake", "--class", "missing-cleanup", "--evidence", "forgot cleanup in user-written effect")
            self.assertEqual(json.loads(result.stdout)["mistake_patterns"]["missing-cleanup"]["count"], 1)
            result = self.cli(project, "mistake", "--class", "missing-cleanup", "--evidence", "api_key was exposed", check=False)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
