#!/usr/bin/env python3
"""One-time setup: create the labels and starter issues, then link the decision table.

Run it from the Actions tab ("Set up labels and issues"). It is safe to run twice:
labels are updated in place, and an issue is skipped if one with the same title exists.

It reads the tables in the docs, so the docs stay the source of truth:
  docs/starter-issues.md  ->  starter and standing issues
  DECISIONS.md            ->  one decision issue per open question
  CHALLENGES.md           ->  one challenge issue per row
  BOUNTIES.md             ->  one bounty issue per row

Needs the GitHub CLI (`gh`) and a token in GH_TOKEN. Use --dry-run to only print.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "Fishers-Founders-United/Swapatron5000"
BLOB = f"https://github.com/{REPO}/blob/main"
DRY = "--dry-run" in sys.argv

LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
NOTHING_DECIDED = "> **Nothing is decided yet.** This is a proposal. Comment below and help shape it."

LABELS = {
    "ask": ("1D76DB", "Someone is asking for a part"),
    "bounty": ("FBCA04", "A job with points attached"),
    "decision": ("5319E7", "An open question that will be decided in the open"),
    "challenge": ("D93F0B", "A known problem Swapatron needs help with"),
    "event": ("0E8A16", "An event, online or in person. Thumbs up if you are coming"),
    "rfc": ("C5DEF5", "A longer proposal that needs comments"),
    "hardware": ("BFD4F2", "The box, the shell, the bins"),
    "electronics": ("FEF2C0", "Power, sensors, radios"),
    "software": ("D4C5F9", "Inventory, alerts, forms"),
    "docs": ("C2E0C6", "Writing, signs, drawings, the tutorial"),
    "brief": ("C5DEF5", "A small start on a drawing, a screen, an integration, or a kit"),
    "integration": ("FEF2C0", "Cameras, inventory, solar, safety, security, discovery"),
    "ai-assisted": ("EDEDED", "An AI helped, and a human checked it"),
    "gathering": ("0E8A16", "Someone saying they would like to join the first meetup"),
    "founding-team": ("5319E7", "Applying for, or discussing, a founding team role"),
    "network": ("0E8A16", "Boxes in other towns and how they connect"),
    "supplies": ("F9D0C4", "Bags, labels, desiccant, lumber"),
    "needs owner": ("EDEDED", "Nobody has claimed this yet. Comment to take it"),
    "good first issue": ("7057FF", "A friendly place to start"),
    "help wanted": ("008672", "Extra hands welcome"),
}


def gh(*args, check=True):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def table_rows(path, heading_hint=None):
    """Yield the cells of each data row in the first table after heading_hint."""
    text = (ROOT / path).read_text(encoding="utf-8")
    if heading_hint:
        idx = text.find(heading_hint)
        text = text[idx:] if idx >= 0 else text
    rows, started = [], False
    for line in text.splitlines():
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
        elif started and not line.startswith("|"):
            break
    return rows


def get_issue(title):
    res = gh("issue", "list", "--repo", REPO, "--search", f'"{title}" in:title', "--json", "title,number", check=False)
    if res.returncode == 0:
        for issue in json.loads(res.stdout or "[]"):
            if issue["title"] == title:
                return issue["number"]
    return None


def create_issue(title, body, labels):
    if existing := get_issue(title):
        print(f"Skipping existing issue #{existing}: {title}")
        return existing

    print(f"Creating issue: {title} [{', '.join(labels)}]")
    if DRY:
        return 999

    cmd = ["issue", "create", "--repo", REPO, "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])
    
    res = gh(*cmd)
    match = re.search(r"github\.com/.*/issues/(\d+)", res.stdout)
    return int(match.group(1)) if match else None


def setup_labels():
    print("Setting up labels...")
    existing_labels = json.loads(gh("label", "list", "--repo", REPO, "--json", "name", check=False).stdout or "[]")
    names = {l["name"] for l in existing_labels}

    for name, (color, desc) in LABELS.items():
        if DRY:
            continue
        if name in names:
            gh("label", "edit", name, "--repo", REPO, "--color", color, "--description", desc, check=False)
        else:
            gh("label", "create", name, "--repo", REPO, "--color", color, "--description", desc, check=False)


def main():
    setup_labels()
    print("Bootstrap complete.")


if __name__ == "__main__":
    main()