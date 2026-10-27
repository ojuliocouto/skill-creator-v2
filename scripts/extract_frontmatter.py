#!/usr/bin/env python3
"""Extract YAML frontmatter from SKILL.md files without PyYAML dependency."""

import re
import sys
import json
from pathlib import Path

# Windows consoles default to cp1252; force UTF-8 so accents and symbols never crash output.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")



def extract_frontmatter(filepath: str) -> dict:
    """Parse YAML frontmatter between --- delimiters using regex."""
    text = Path(filepath).read_text(encoding="utf-8-sig", errors="replace")

    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    raw = match.group(1)
    result = {}
    current_key = None
    current_list = None

    for line in raw.split("\n"):
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item under current key
        if stripped.startswith("- ") and current_key:
            item = stripped[2:].strip()
            # Check if it's a nested dict (e.g., "- skill: foo")
            if ": " in item and current_key in ("pairs-with", "pairs_with"):
                # Accumulate nested dict
                if current_list is None:
                    current_list = []
                if not current_list or isinstance(current_list[-1], dict) and "reason" in current_list[-1]:
                    current_list.append({})
                k, v = item.split(": ", 1)
                current_list[-1][k.strip()] = v.strip().strip('"').strip("'")
            else:
                if current_list is None:
                    current_list = []
                current_list.append(item.strip('"').strip("'"))
            result[current_key] = current_list
            continue

        # Nested key-value under a list item (e.g., "    reason: ...")
        if line.startswith("    ") and current_key and current_list:
            if ": " in stripped:
                k, v = stripped.split(": ", 1)
                if current_list and isinstance(current_list[-1], dict):
                    current_list[-1][k.strip()] = v.strip().strip('"').strip("'")
            continue

        # Top-level key: value
        if ": " in stripped or stripped.endswith(":"):
            current_list = None
            if ": " in stripped:
                key, val = stripped.split(": ", 1)
                current_key = key.strip()
                val = val.strip()
                # Multi-line string indicators
                if val in (">", "|", ">-", "|-"):
                    result[current_key] = ""
                    continue
                # Remove quotes
                val = val.strip('"').strip("'")
                result[current_key] = val
            else:
                current_key = stripped.rstrip(":")
                result[current_key] = []

    return result


def extract_body(filepath: str) -> str:
    """Extract everything after the frontmatter."""
    text = Path(filepath).read_text(encoding="utf-8-sig", errors="replace")
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.DOTALL)
    if match:
        return text[match.end():]
    return text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract_frontmatter.py <SKILL.md> [--body] [--json]")
        sys.exit(1)

    filepath = sys.argv[1]
    show_body = "--body" in sys.argv
    as_json = "--json" in sys.argv

    if not Path(filepath).exists():
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(1)

    fm = extract_frontmatter(filepath)

    if show_body:
        body = extract_body(filepath)
        fm["_body_preview"] = body[:500] + ("..." if len(body) > 500 else "")

    if as_json:
        print(json.dumps(fm, indent=2, ensure_ascii=False))
    else:
        for k, v in fm.items():
            if isinstance(v, list):
                print(f"{k}:")
                for item in v:
                    if isinstance(item, dict):
                        print(f"  - {item}")
                    else:
                        print(f"  - {item}")
            else:
                display = v[:100] + "..." if isinstance(v, str) and len(v) > 100 else v
                print(f"{k}: {display}")
