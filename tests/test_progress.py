import datetime as dt
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


    def test_sessions_merge_per_day_and_track_shaky(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            for name in ("closures", "closures", "debounce"): self.cli(project, "teach", "--concept", name, "--stack", "javascript")
            self.cli(project, "result", "--concept", "debounce", "--outcome", "wrong")
            sessions = self.state(project)["sessions"]
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["concepts"], ["closures", "debounce"]); self.assertEqual(sessions[0]["shaky"], ["debounce"])
            self.cli(project, "result", "--concept", "debounce", "--outcome", "correct")
            self.assertEqual(self.state(project)["sessions"][0]["shaky"], [])

    def test_stats_streak_and_mastery(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            self.cli(project, "teach", "--concept", "sql joins", "--stack", "sql")
            for _ in range(3): self.cli(project, "result", "--concept", "sql-joins", "--outcome", "correct")
            data = self.state(project); now = dt.date.today()
            data["sessions"] += [{"date": (now - dt.timedelta(days=d)).isoformat(), "concepts": [], "shaky": []} for d in (1, 2, 5)]
            (project / ".vibe-learn/state.json").write_text(json.dumps(data))
            stats = json.loads(self.cli(project, "stats").stdout)
            self.assertEqual(stats["streak_days"], 3); self.assertEqual(stats["learning_days"], 4)
            self.assertEqual(stats["mastered"], 1); self.assertEqual(stats["days_since_last_session"], 0)

    def test_stats_streak_breaks_after_gap(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init"); data = self.state(project)
            data["sessions"] = [{"date": (dt.date.today() - dt.timedelta(days=3)).isoformat(), "concepts": [], "shaky": []}]
            (project / ".vibe-learn/state.json").write_text(json.dumps(data))
            stats = json.loads(self.cli(project, "stats").stdout)
            self.assertEqual(stats["streak_days"], 0); self.assertEqual(stats["days_since_last_session"], 3)

    def test_export_anki_csv_and_markdown(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            self.cli(project, "teach", "--concept", "res.ok check", "--stack", "javascript", "--note", "fetch only throws on network failure")
            self.cli(project, "teach", "--concept", "effect cleanup", "--stack", "react")
            self.cli(project, "result", "--concept", "effect-cleanup", "--outcome", "partial")
            result = json.loads(self.cli(project, "export").stdout)
            lines = Path(result["path"]).read_text().splitlines()
            self.assertEqual(lines[:3], ["#separator:tab", "#html:false", "#tags column:3"])
            self.assertEqual(lines[3].split("\t")[2], "vibe-learn react shaky")
            self.assertIn("fetch only throws on network failure", lines[4])
            result = json.loads(self.cli(project, "export", "--format", "csv", "--shaky-only").stdout)
            self.assertEqual(result["exported"], 1)
            self.assertEqual(len(Path(result["path"]).read_text().splitlines()), 2)
            out = project / "cards.md"
            self.cli(project, "export", "--format", "md", "--out", str(out))
            self.assertIn("<details>", out.read_text())

    def test_note_rejects_secrets_and_is_capped(self):
        with tempfile.TemporaryDirectory() as path:
            project = Path(path); self.cli(project, "init")
            for i in range(5): self.cli(project, "teach", "--concept", "caching", "--stack", "go", "--note", f"takeaway {i}")
            self.assertEqual(self.state(project)["concepts"]["caching"]["notes"], ["takeaway 2", "takeaway 3", "takeaway 4"])
            result = self.cli(project, "teach", "--concept", "caching", "--stack", "go", "--note", "password is hunter2", check=False)
            self.assertNotEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()
