#!/usr/bin/env python3
"""Build the contributor celebrations from contributions.csv.

Run from the repository root:  python3 scripts/build_wall.py
Uses only the Python standard library.

It writes three things:
  1. CONTRIBUTORS.md           the full wall and leaderboard
  2. README.md                 the top five, between the WALL markers
  3. index.html                the top five, between the WALL markers

contributions.csv columns: date, username, type, description, points
The points column is optional. A blank or missing value counts as 1.
"""
import csv
import html
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "contributions.csv"
WALL = ROOT / "CONTRIBUTORS.md"
README = ROOT / "README.md"
PAGE = ROOT / "index.html"

START = "<!-- WALL:START -->"
END = "<!-- WALL:END -->"
REPO_URL = "https://github.com/Fishers-Founders-United/Swapatron5000"

TYPES = {
    "part": "Parts and supplies",
    "build": "Building",
    "code": "Code and electronics",
    "docs": "Docs and signs",
    "upkeep": "Box upkeep",
    "idea": "Ideas",
}
ALLOWED_POINTS = {1, 2, 3, 5}
LEVELS = [(30, "Architect"), (15, "Builder"), (5, "Tinkerer"), (1, "Spark")]
# badge name, contribution type, how many contributions of that type
BADGES = [
    ("Giver", "part", 3),
    ("Maker", "build", 2),
    ("Coder", "code", 2),
    ("Scribe", "docs", 2),
    ("Keeper", "upkeep", 4),
    ("Thinker", "idea", 3),
]
ALL_ROUNDER_TYPES = 4
TOP_N = 10
TOP_FIVE = 5
LATEST_N = 5

# Placeholders for the top five. Each one is replaced by a real person as
# soon as there are enough contributors to fill its spot.
ARCHETYPES = [
    ("The Drawer Emptier",
     "Has a drawer full of spare dev boards and a guilty conscience."),
    ("The Doodler",
     "Draws a box on a napkin and changes everything."),
    ("The Skeptic",
     "Says \"this won't work because...\" and is right, which is why it ends up working."),
    ("The First-Timer",
     "Has never touched GitHub or a soldering iron, and shows up anyway."),
    ("The Keeper",
     "Checks on Swapatron every week and expects no applause. Gets applause."),
]

USERNAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def load():
    """TODO: Add docstring for load."""
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as f:
        for line_no, row in enumerate(csv.DictReader(f), start=2):
            user = (row.get("username") or "").strip().lstrip("@")
            kind = (row.get("type") or "").strip().lower()
            if not user:
                continue
            if not USERNAME.match(user):
                raise SystemExit(
                    f"contributions.csv line {line_no}: '{user}' is not a "
                    f"valid GitHub username."
                )
            if kind not in TYPES:
                raise SystemExit(
                    f"contributions.csv line {line_no}: unknown type '{kind}'. "
                    f"Use one of: {', '.join(TYPES)}"
                )
            raw = (row.get("points") or "").strip()
            try:
                points = int(raw) if raw else 1
            except ValueError:
                points = -1
            if points not in ALLOWED_POINTS:
                raise SystemExit(
                    f"contributions.csv line {line_no}: points must be 1, 2, 3, "
                    f"or 5 (or blank for 1). Found '{raw}'."
                )
            if kind == "part" and points != 1:
                raise SystemExit(
                    f"contributions.csv line {line_no}: giving a part is always "
                    f"1 point, whatever it cost."
                )
            rows.append({
                "user": user,
                "kind": kind,
                "points": points,
                "date": (row.get("date") or "").strip(),
                "what": " ".join((row.get("description") or "").split()),
            })
    return rows


def level_for(points):
    """TODO: Add docstring for level_for."""
    for threshold, name in LEVELS:
        if points >= threshold:
            return name
    return ""


def badges_for(kind_counts):
    """TODO: Add docstring for badges_for."""
    earned = [name for name, kind, need in BADGES if kind_counts[kind] >= need]
    if sum(1 for kind in TYPES if kind_counts[kind]) >= ALL_ROUNDER_TYPES:
        earned.append("All-rounder")
    return earned


def tally(rows):
    """TODO: Add docstring for tally."""
    points = Counter()
    counts = Counter()
    kinds = defaultdict(Counter)
    for row in rows:
        points[row["user"]] += row["points"]
        counts[row["user"]] += 1
        kinds[row["user"]][row["kind"]] += 1
    ranked = sorted(points.items(), key=lambda item: (-item[1], item[0].lower()))
    return points, counts, kinds, ranked


def latest(rows):
    """Most recent contributions first. Later lines win ties."""
    indexed = list(enumerate(rows))
    indexed.sort(key=lambda pair: (pair[1]["date"], pair[0]), reverse=True)
    return [row for _, row in indexed[:LATEST_N]]


def md_cell(text):
    """TODO: Add docstring for md_cell."""
    return html.escape(text, quote=False).replace("|", "/")


# ---------- CONTRIBUTORS.md ----------

def render_wall(rows):
    """TODO: Add docstring for render_wall."""
    points, counts, kinds, ranked = tally(rows)
    out = [
        "# Contributors Wall",
        "",
        "Everyone who has fed, built, drawn, questioned, or looked after "
        "Swapatron. Thank you.",
        "",
        "This page is built automatically from `contributions.csv`. "
        "Do not edit it by hand. See [BOUNTIES.md](BOUNTIES.md) for how "
        "points, levels, and badges work.",
        "",
    ]
    if not points:
        out += [
            "Nobody is on the wall yet. Be the first!",
            "",
            "## Swapatron is waiting for",
            "",
        ]
        for name, line in ARCHETYPES:
            out.append(f"- **{name}.** {line}")
        out.append("")
        return "\n".join(out)

    out += [
        "## Leaderboard",
        "",
        "Points are for fun and for thanks. Giving a part is always 1 point, "
        "whatever it cost.",
        "",
        "| Rank | Contributor | Points | Level | Contributions |",
        "|---|---|---|---|---|",
    ]
    rank = 0
    previous = None
    for position, (user, pts) in enumerate(ranked[:TOP_N], start=1):
        if pts != previous:
            rank = position
            previous = pts
        out.append(
            f"| {rank} | [@{user}](https://github.com/{user}) | {pts} | "
            f"{level_for(pts)} | {counts[user]} |"
        )

    out += ["", "## The wall", ""]
    for user in sorted(points, key=str.lower):
        helped = ", ".join(TYPES[kind] for kind in TYPES if kinds[user][kind])
        line = (
            f"- [@{user}](https://github.com/{user}) "
            f"({level_for(points[user])}): {helped}"
        )
        earned = badges_for(kinds[user])
        if earned:
            line += ". Badges: " + ", ".join(earned)
        out.append(line)
    out.append("")
    return "\n".join(out)


# ---------- README.md block ----------

def render_readme_block(rows):
    """TODO: Add docstring for render_readme_block."""
    points, counts, kinds, ranked = tally(rows)
    top = ranked[:TOP_FIVE]
    out = [
        "## Swapatron's favorite humans",
        "",
    ]
    if top:
        out.append(
            "These people made Swapatron real. Thank you, loudly."
        )
    else:
        out.append(
            "Nobody has fed Swapatron yet, so it is imagining who will. "
            "Each spot below is replaced by a real person as soon as someone "
            "earns it."
        )
    out += ["", "| # | Who | Points |", "|---|---|---|"]
    for slot in range(TOP_FIVE):
        if slot < len(top):
            user, pts = top[slot]
            out.append(
                f"| {slot + 1} | <img src=\"https://github.com/{user}.png?size=48\" "
                f"width=\"24\" height=\"24\" alt=\"\"> "
                f"**[@{user}](https://github.com/{user})** "
                f"({level_for(pts)}) | {pts} |"
            )
        else:
            name, line = ARCHETYPES[slot]
            out.append(
                f"| {slot + 1} | *Waiting for:* **{name}.** {md_cell(line)} | ? |"
            )
    recent = latest(rows)
    if recent:
        out += ["", "**Latest thank-yous**", ""]
        for row in recent:
            what = f" for {md_cell(row['what'])}" if row["what"] else ""
            out.append(
                f"- Thank you [@{row['user']}](https://github.com/{row['user']})"
                f"{what}"
            )
    out += [
        "",
        "See everyone on the [Contributors Wall](CONTRIBUTORS.md), and "
        "[how to get your name here](BOUNTIES.md).",
    ]
    return "\n".join(out)


# ---------- index.html block ----------

def render_page_block(rows):
    """TODO: Add docstring for render_page_block."""
    points, counts, kinds, ranked = tally(rows)
    top = ranked[:TOP_FIVE]
    pad = "    "
    out = [f"{pad}<h2>Swapatron's favorite humans</h2>"]
    if top:
        out.append(f"{pad}<p>These people made Swapatron real. Thank you, loudly.</p>")
    else:
        out.append(
            f"{pad}<p>Nobody has fed Swapatron yet, so it is imagining who will. "
            f"Each spot is replaced by a real person as soon as someone earns it.</p>"
        )
    out.append(f'{pad}<ol class="humans">')
    for slot in range(TOP_FIVE):
        if slot < len(top):
            user, pts = top[slot]
            safe = html.escape(user)
            word = "point" if pts == 1 else "points"
            out.append(
                f'{pad}  <li><img src="https://github.com/{safe}.png?size=96" '
                f'width="44" height="44" alt="" loading="lazy">'
                f'<span><a href="https://github.com/{safe}"><strong>@{safe}</strong></a>'
                f'<br>{html.escape(level_for(pts))}, {pts} {word}</span></li>'
            )
        else:
            name, line = ARCHETYPES[slot]
            out.append(
                f'{pad}  <li class="waiting"><span class="ghost" aria-hidden="true">?</span>'
                f'<span><strong>Waiting for: {html.escape(name)}</strong>'
                f'<br>{html.escape(line)}</span></li>'
            )
    out.append(f"{pad}</ol>")
    recent = latest(rows)
    if recent:
        out.append(f'{pad}<p class="thanks-title">Latest thank-yous</p>')
        out.append(f'{pad}<ul class="thanks">')
        for row in recent:
            safe = html.escape(row["user"])
            what = f" for {html.escape(row['what'])}" if row["what"] else ""
            out.append(
                f'{pad}  <li>Thank you <a href="https://github.com/{safe}">@{safe}</a>{what}</li>'
            )
        out.append(f"{pad}</ul>")
    out.append(
        f'{pad}<a class="btn alt" href="{REPO_URL}/blob/main/BOUNTIES.md">'
        f"Get your name here</a>"
    )
    return "\n".join(out)


def replace_block(path, block):
    """TODO: Add docstring for replace_block."""
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print(f"Skipped {path.name}: WALL markers not found")
        return
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    path.write_text(f"{before}{START}\n{block}\n{END}{after}", encoding="utf-8")
    print(f"Updated {path.name}")


def main():
    """TODO: Add docstring for main."""
    rows = load()
    WALL.write_text(render_wall(rows), encoding="utf-8")
    print(f"Wrote {WALL.name}")
    replace_block(README, render_readme_block(rows))
    replace_block(PAGE, render_page_block(rows))


if __name__ == "__main__":
    main()
