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
        elif started and not line.strip():
            break
    return rows


def clean_title(raw):
    """Turn a markdown link [Title](url) or plain text into a clean title string."""
    m = LINK_RE.search(raw)
    if m:
        return m.group(1)
    return raw.strip()


def ensure_labels():
    print("Ensuring labels exist...")
    existing_json = gh("label", "list", "--json", "name", "-R", REPO)
    existing = {item["name"] for item in json.loads(existing_json.stdout)}
    
    for name, (color, desc) in LABELS.items():
        if DRY:
            print(f"  [dry-run] Would ensure label '{name}' (color #{color})")
            continue
        if name in existing:
            gh("label", "edit", name, "--color", color, "--description", desc, "-R", REPO, check=False)
        else:
            gh("label", "create", name, "--color", color, "--description", desc, "-R", REPO, check=False)


def create_issue(title, body, labels):
    if DRY:
        print(f"  [dry-run] Would create issue: '{title}' with labels {labels}")
        return
    
    # Check if issue already exists
    existing = gh("issue", "list", "--search", f'"{title}" in:title', "--json", "title", "-R", REPO)
    issues = json.loads(existing.stdout)
    if any(i["title"] == title for i in issues):
        print(f"  Skipping existing issue: '{title}'")
        return

    label_args = []
    for l in labels:
        label_args.extend(["--label", l])
    
    gh("issue", "create", "--title", title, "--body", body, *label_args, "-R", REPO)
    time.sleep(1) # Be nice to GitHub API


def setup_starter_issues():
    print("Setting up starter issues from docs/starter-issues.md...")
    rows = table_rows("docs/starter-issues.md")
    for cells in rows:
        if len(cells) < 3:
            continue
        title = clean_title(cells[0])
        desc = cells[1]
        labels_str = cells[2]
        labels = [l.strip() for l in labels_str.split(",") if l.strip()]
        body = f"{desc}\n\nRead more in [starter-issues.md]({BLOB}/docs/starter-issues.md)."
        create_issue(title, body, labels)


def setup_decisions():
    print("Setting up decision issues from DECISIONS.md...")
    rows = table_rows("DECISIONS.md")
    for cells in rows:
        if len(cells) < 2:
            continue
        title = clean_title(cells[0])
        status = cells[1]
        body = f"{NOTHING_DECIDED}\n\nStatus: {status}\n\nRead more in [DECISIONS.md]({BLOB}/DECISIONS.md)."
        create_issue(title, body, ["decision", "needs owner"])


def setup_challenges():
    print("Setting up challenge issues from CHALLENGES.md...")
    rows = table_rows("CHALLENGES.md")
    for cells in rows:
        if len(cells) < 2:
            continue
        title = clean_title(cells[0])
        desc = cells[1]
        body = f"{desc}\n\nRead more in [CHALLENGES.md]({BLOB}/CHALLENGES.md)."
        create_issue(title, body, ["challenge", "help wanted"])


def setup_bounties():
    print("Setting up bounty issues from BOUNTIES.md...")
    rows = table_rows("BOUNTIES.md")
    for cells in rows:
        if len(cells) < 3:
            continue
        title = clean_title(cells[0])
        points = cells[1]
        desc = cells[2]
        body = f"**Points:** {points}\n\n{desc}\n\nRead more in [BOUNTIES.md]({BLOB}/BOUNTIES.md)."
        create_issue(title, body, ["bounty", "needs owner"])


def main():
    if not DRY and not Path(".git").exists() and "GH_TOKEN" not in sys.modules:
        # Just a sanity check reminder
        pass
    
    ensure_labels()
    setup_starter_issues()
    setup_decisions()
    setup_challenges()
    setup_bounties()
    print("Bootstrap complete!")


if __name__ == "__main__":
    main()