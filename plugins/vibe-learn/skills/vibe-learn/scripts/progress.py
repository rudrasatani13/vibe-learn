#!/usr/bin/env python3
"""Deterministic, privacy-preserving progress state for vibe-learn."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

SCHEMA_VERSION = 2
MAX_SESSIONS = 20
MAX_NOTE = 240
OUTCOMES = {"correct", "partial", "wrong"}
LEVELS = {"beginner", "intermediate", "advanced"}
DENSITIES = {"quiet", "normal", "dense"}
MISTAKE_CLASSES = {
    "missing-error-handling", "null-state-assumption", "async-race-or-stale-result",
    "missing-cleanup", "sequential-work-that-can-be-parallel",
    "authorization-vs-authentication-confusion", "implementation-coupled-test",
    "unvalidated-input", "state-ownership-confusion", "unsafe-secret-boundary",
}
SECRET_RE = re.compile(r"(?:api[_-]?key|secret|token|password|-----BEGIN|sk-[A-Za-z0-9])", re.I)


def today() -> dt.date:
    return dt.date.today()


def iso_date(value: dt.date) -> str:
    return value.isoformat()


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid date: {value!r}") from exc


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    if not value:
        raise ValueError("concept name must contain letters or numbers")
    return value[:80].rstrip("-")


def safe_text(value: str, field: str) -> str:
    value = str(value).strip()
    if not value or len(value) > MAX_NOTE:
        raise ValueError(f"{field} must be 1-{MAX_NOTE} characters")
    if SECRET_RE.search(value):
        raise ValueError(f"{field} looks like it may contain a secret")
    return value


def empty_state() -> dict:
    return {"schema_version": SCHEMA_VERSION, "profile": {
        "level": "intermediate", "density": "normal", "interview": False,
        "focus": None, "goal": None,
    }, "concepts": {}, "mistake_patterns": {}, "sessions": []}


def paths(project: Path) -> tuple[Path, Path, Path]:
    directory = project / ".vibe-learn"
    return directory / "state.json", directory / "progress.md", directory / "progress.v1.2.backup.md"


def validate_state(state: object) -> dict:
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"state schema_version must be {SCHEMA_VERSION}")
    if not isinstance(state.get("profile"), dict) or not isinstance(state.get("concepts"), dict):
        raise ValueError("state must contain profile and concepts objects")
    profile = state["profile"]
    if profile.get("level") not in LEVELS or profile.get("density") not in DENSITIES:
        raise ValueError("profile has an invalid level or density")
    if not isinstance(profile.get("interview"), bool):
        raise ValueError("profile.interview must be boolean")
    if not isinstance(state.get("mistake_patterns", {}), dict) or not isinstance(state.get("sessions", []), list):
        raise ValueError("mistake_patterns and sessions must have valid types")
    for slug, concept in state["concepts"].items():
        if slug != slugify(slug) or not isinstance(concept, dict):
            raise ValueError(f"invalid concept: {slug}")
        required = ("name", "stack", "times_taught", "times_quizzed", "interval_days", "shaky")
        if any(key not in concept for key in required):
            raise ValueError(f"missing concept fields for {slug}")
        if not isinstance(concept["name"], str) or not isinstance(concept["stack"], str):
            raise ValueError(f"invalid text fields for {slug}")
        if not isinstance(concept["times_taught"], int) or not isinstance(concept["times_quizzed"], int):
            raise ValueError(f"invalid counters for {slug}")
        if not isinstance(concept["shaky"], bool):
            raise ValueError(f"invalid shaky flag for {slug}")
        for key in ("first_seen", "last_seen", "next_review"):
            parse_date(concept.get(key))
        if concept.get("last_result") not in (None, "correct", "partial", "wrong"):
            raise ValueError(f"invalid last_result for {slug}")
        if not isinstance(concept.get("interval_days"), int) or not 1 <= concept["interval_days"] <= 14:
            raise ValueError(f"invalid interval_days for {slug}")
    return state


def load_state(project: Path, create: bool = False) -> dict:
    state_path, _, _ = paths(project)
    if not state_path.exists():
        if create:
            state = empty_state()
            save_state(project, state)
            return state
        raise FileNotFoundError(f"state not found: {state_path}")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read state safely: {exc}") from exc
    return validate_state(state)


def save_state(project: Path, state: dict) -> None:
    validate_state(state)
    state_path, _, _ = paths(project)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="state.", suffix=".tmp", dir=state_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, state_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def concept(state: dict, name: str, stack: str) -> tuple[str, dict]:
    slug = slugify(name)
    now = today()
    item = state["concepts"].get(slug)
    if item is None:
        item = {"name": safe_text(name, "name"), "stack": safe_text(stack, "stack"),
                "first_seen": iso_date(now), "last_seen": iso_date(now),
                "next_review": iso_date(now + dt.timedelta(days=1)), "interval_days": 1,
                "times_taught": 0, "times_quizzed": 0, "last_result": None,
                "shaky": False, "related": [], "notes": []}
        state["concepts"][slug] = item
    item["last_seen"] = iso_date(now)
    item["times_taught"] += 1
    return slug, item


def render(state: dict) -> str:
    profile = state["profile"]
    lines = ["# vibe-learn progress", "", "Generated from `.vibe-learn/state.json`; edit state through the progress CLI.", "",
             "## Status", "", f"- level: {profile['level']}", f"- density: {profile['density']}",
             f"- interview: {str(profile['interview']).lower()}", "", "## Concepts", ""]
    for slug, item in sorted(state["concepts"].items(), key=lambda pair: (pair[1]["next_review"], pair[0])):
        lines.extend([f"### {slug}", f"- name: {item['name']}", f"- stack: {item['stack']}",
                      f"- first_seen: {item['first_seen']}", f"- last_seen: {item['last_seen']}",
                      f"- times_taught: {item['times_taught']}", f"- times_quizzed: {item['times_quizzed']}",
                      f"- last_result: {item['last_result'] or 'none'}", f"- next_review: {item['next_review']}",
                      f"- interval_days: {item['interval_days']}", f"- shaky: {str(item['shaky']).lower()}",
                      "- notes: " + "; ".join(item.get("notes", [])), ""])
    lines.extend(["## Recurring mistakes", ""])
    for slug, item in sorted(state["mistake_patterns"].items(), key=lambda pair: (-pair[1]["count"], pair[0])):
        lines.extend([f"- {slug}: {item['count']} occurrence(s); last_seen: {item['last_seen']}", "  - evidence: " + "; ".join(item["evidence"]), ""])
    lines.extend(["## Session log", ""])
    for session in state["sessions"]:
        lines.append(f"- {session['date']}: {', '.join(session.get('concepts', [])) or 'no concepts'}; shaky: {', '.join(session.get('shaky', [])) or 'none'}")
    return "\n".join(lines).rstrip() + "\n"


def write_render(project: Path, state: dict) -> None:
    _, report, _ = paths(project)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render(state), encoding="utf-8")


def migrate_markdown(project: Path, dry_run: bool) -> dict:
    state_path, report, backup = paths(project)
    if state_path.exists():
        raise ValueError("state.json already exists; migration is unnecessary")
    if not report.exists():
        raise FileNotFoundError("legacy progress.md not found")
    text = report.read_text(encoding="utf-8")
    state = empty_state()
    meta = dict(re.findall(r"^- ([a-z_]+): (.+)$", text, re.M))
    if meta.get("level") in LEVELS: state["profile"]["level"] = meta["level"]
    if meta.get("density") in DENSITIES: state["profile"]["density"] = meta["density"]
    if meta.get("interview") in ("true", "false"): state["profile"]["interview"] = meta["interview"] == "true"
    blocks = re.split(r"(?=^### )", text, flags=re.M)
    for block in blocks:
        match = re.match(r"^### ([a-z0-9][a-z0-9-]*)\n(.*?)(?=^### |\Z)", block, re.S | re.M)
        if not match: continue
        slug, body = match.groups()
        fields = dict(re.findall(r"^- ([a-z_]+): (.*)$", body, re.M))
        if not fields.get("name"): continue
        normalized = slugify(fields["name"])
        item = {"name": safe_text(fields["name"], "name"), "stack": safe_text(fields.get("stack", "unknown"), "stack"),
                "first_seen": fields.get("first_seen", iso_date(today())), "last_seen": fields.get("last_seen", iso_date(today())),
                "times_taught": int(fields.get("times_taught", 0)), "times_quizzed": int(fields.get("times_quizzed", 0)),
                "last_result": None if fields.get("last_result", "none") == "none" else fields.get("last_result"),
                "next_review": fields.get("next_review", iso_date(today() + dt.timedelta(days=1))),
                "interval_days": int(fields.get("interval_days", 1)), "shaky": fields.get("shaky", "false") == "true",
                "related": [], "notes": [] if not fields.get("notes") else [safe_text(fields["notes"], "notes")]}
        state["concepts"][normalized] = item
    validate_state(state)
    if not dry_run:
        shutil.copy2(report, backup)
        save_state(project, state)
        write_render(project, state)
    return {"concepts": len(state["concepts"]), "dry_run": dry_run, "backup": str(backup) if not dry_run else None}


def command(args: argparse.Namespace) -> object:
    project = Path(args.project).expanduser().resolve()
    if args.command == "init":
        state = load_state(project, create=True); write_render(project, state); return {"initialized": True}
    if args.command == "migrate": return migrate_markdown(project, args.dry_run)
    state = load_state(project)
    if args.command == "validate": validate_state(state); return {"valid": True, "schema_version": SCHEMA_VERSION}
    if args.command == "render": write_render(project, state); return {"rendered": True}
    if args.command == "teach":
        slug, _ = concept(state, args.name, args.stack)
        state["sessions"].insert(0, {"date": iso_date(today()), "concepts": [slug], "shaky": []})
    elif args.command == "result":
        if args.concept not in state["concepts"]: raise ValueError(f"unknown concept: {args.concept}")
        if args.outcome not in OUTCOMES: raise ValueError("outcome must be correct, partial, or wrong")
        item = state["concepts"][args.concept]; item["times_quizzed"] += 1; item["last_result"] = args.outcome
        if args.outcome == "wrong": interval, shaky = 1, True
        elif args.outcome == "partial": interval, shaky = 2, True
        else: interval, shaky = min(14, max(2, item["interval_days"] * 2)), False
        item["interval_days"] = interval; item["next_review"] = iso_date(today() + dt.timedelta(days=interval)); item["shaky"] = shaky
    elif args.command == "mistake":
        if args.mistake_class not in MISTAKE_CLASSES: raise ValueError("unknown mistake class")
        evidence = safe_text(args.evidence, "evidence"); item = state["mistake_patterns"].setdefault(args.mistake_class, {"count": 0, "first_seen": iso_date(today()), "last_seen": iso_date(today()), "evidence": []})
        item["count"] += 1; item["last_seen"] = iso_date(today()); item["evidence"] = (item["evidence"] + [evidence])[-3:]
    elif args.command == "profile":
        if args.level: state["profile"]["level"] = args.level
        if args.density: state["profile"]["density"] = args.density
    elif args.command == "due":
        due = [dict(slug=k, **v) for k, v in state["concepts"].items() if v["shaky"] or parse_date(v["next_review"]) <= today()]
        return sorted(due, key=lambda x: (not x["shaky"], x["next_review"]))[:args.limit]
    elif args.command == "recap":
        return {"concepts": [s for session in state["sessions"] if session["date"] == iso_date(today()) for s in session.get("concepts", [])], "shaky": [k for k, v in state["concepts"].items() if v["shaky"]]}
    else: raise ValueError(f"unsupported command: {args.command}")
    state["sessions"] = state["sessions"][:MAX_SESSIONS]; save_state(project, state); write_render(project, state); return state


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--project", default="."); sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init"); m = sub.add_parser("migrate"); m.add_argument("--dry-run", action="store_true")
    sub.add_parser("validate"); sub.add_parser("render")
    t = sub.add_parser("teach"); t.add_argument("--concept", dest="name", required=True); t.add_argument("--name", dest="name_override"); t.add_argument("--stack", required=True)
    # --concept is the documented alias; --name is accepted for compatibility with the plan interface.
    t.set_defaults(name=None)
    r = sub.add_parser("result"); r.add_argument("--concept", required=True); r.add_argument("--outcome", required=True)
    mm = sub.add_parser("mistake"); mm.add_argument("--class", dest="mistake_class", required=True); mm.add_argument("--evidence", required=True)
    pr = sub.add_parser("profile"); pr.add_argument("--level", choices=sorted(LEVELS)); pr.add_argument("--density", choices=sorted(DENSITIES))
    d = sub.add_parser("due"); d.add_argument("--limit", type=int, default=4)
    sub.add_parser("recap"); return p


def main() -> int:
    try:
        args = parser().parse_args()
        if args.command == "teach": args.name = args.name_override or args.name
        result = command(args); print(json.dumps(result, indent=2, ensure_ascii=False)); return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
