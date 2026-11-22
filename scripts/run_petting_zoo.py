#!/usr/bin/env python3
"""
run_petting_zoo.py

A simple utility to list the habitats defined in docs/petting-zoo.md.
"""

import argparse
import sys
from pathlib import Path


def parse_habitats(md_path: Path):
    """Parse the habitats table from the markdown file."""
    content = md_path.read_text(encoding="utf-8")
    # Find the table starting with | Habitat |
    table_start = content.find("| Habitat |")
    if table_start == -1:
        raise ValueError("Habitat table not found in the markdown file.")
    table_text = content[table_start:]
    # Split into lines
    lines = table_text.splitlines()
    # Skip header and separator
    lines = lines[2:]  # header + separator
    habitats = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3:
            habitat, lives, do = parts[0], parts[1], parts[2]
            habitats.append((habitat, lives, do))
    return habitats


def main():
    parser = argparse.ArgumentParser(description="List petting zoo habitats.")
    parser.add_argument(
        "--md",
        default="docs/petting-zoo.md",
        help="Path to the petting zoo markdown file (default: docs/petting-zoo.md)",
    )
    args = parser.parse_args()
    md_path = Path(args.md)
    if not md_path.is_file():
        print(f"Error: {md_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    try:
        habitats = parse_habitats(md_path)
    except Exception as e:
        print(f"Error parsing habitats: {e}", file=sys.stderr)
        sys.exit(1)
    for habitat, lives, do in habitats:
        print(f"Habitat: {habitat}")
        print(f"  Lives: {lives}")
        print(f"  What you do: {do}")
        print()


if __name__ == "__main__":
    main()
