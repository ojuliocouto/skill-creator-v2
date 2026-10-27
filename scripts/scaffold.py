#!/usr/bin/env python3
"""Scaffold a new skill directory from template."""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Windows consoles default to cp1252; force UTF-8 so accents and symbols never crash output.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


TEMPLATES_DIR = Path(__file__).parent.parent / "references" / "templates"

CATEGORY_MAP = {
    "api": "api-integration",
    "api-integration": "api-integration",
    "workflow": "workflow",
    "analysis": "analysis",
    "creative": "creative",
    "utility": "utility",
}

DEFAULT_STRUCTURE = {
    "api-integration": {
        "dirs": ["scripts", "references"],
        "files": {
            "config.json": '{\n  "api_token": "",\n  "base_url": ""\n}',
            "references/api-payloads.md": "# API Payloads Reference\n\n## Endpoints\n\n## Example Payloads\n",
        },
        "scripts": ["api_client.py"],
    },
    "workflow": {
        "dirs": ["scripts", "references"],
        "files": {},
        "scripts": [],
    },
    "analysis": {
        "dirs": ["scripts", "references"],
        "files": {},
        "scripts": ["analyze.py", "report.py"],
    },
    "creative": {
        "dirs": ["scripts", "references", "assets"],
        "files": {
            "config.json": '{\n  "api_token": "",\n  "output_dir": "/tmp"\n}',
        },
        "scripts": ["generate.py"],
    },
    "utility": {
        "dirs": ["scripts"],
        "files": {},
        "scripts": [],
    },
}


def load_template(category: str) -> str:
    """Load template markdown for category."""
    cat = CATEGORY_MAP.get(category, category)
    template_file = TEMPLATES_DIR / f"{cat}.md"
    if template_file.exists():
        return template_file.read_text(encoding="utf-8-sig")
    return ""


def generate_frontmatter(name: str, description: str, category: str, triggers: list = None, allowed_tools: list = None) -> str:
    """Generate YAML frontmatter."""
    lines = ["---"]
    lines.append(f'name: {name}')
    lines.append(f'description: "{description}"')

    tools = allowed_tools or ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
    lines.append(f'allowed-tools: {", ".join(tools)}')

    if triggers:
        lines.append("triggers:")
        for t in triggers:
            lines.append(f"  - {t}")

    lines.append("---")
    return "\n".join(lines)


def scaffold(name: str, category: str, output: str = None, description: str = "", triggers: list = None, dry_run: bool = False) -> dict:
    """Create skill directory structure."""
    cat = CATEGORY_MAP.get(category, category)
    structure = DEFAULT_STRUCTURE.get(cat, DEFAULT_STRUCTURE["workflow"])

    if output:
        skill_dir = Path(output)
    else:
        skill_dir = Path.home() / ".claude" / "skills" / name

    created = {"dir": str(skill_dir), "files": [], "dirs": []}

    if dry_run:
        print(f"[DRY RUN] Would create: {skill_dir}/")
        print(f"  SKILL.md")
        for d in structure["dirs"]:
            print(f"  {d}/")
        for f in structure["files"]:
            print(f"  {f}")
        for s in structure["scripts"]:
            print(f"  scripts/{s}")
        return created

    # Create dirs
    skill_dir.mkdir(parents=True, exist_ok=True)
    for d in structure["dirs"]:
        (skill_dir / d).mkdir(exist_ok=True)
        created["dirs"].append(d)

    # Create SKILL.md with frontmatter + template
    frontmatter = generate_frontmatter(name, description or f"Skill: {name}", category, triggers)
    template = load_template(cat)

    skill_md = frontmatter + "\n\n" + template if template else frontmatter + "\n\n# " + name.replace("-", " ").title() + "\n\n## TODO\n- [ ] Implement skill logic\n"
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    created["files"].append("SKILL.md")

    # Create static files
    for fpath, content in structure["files"].items():
        target = skill_dir / fpath
        target.parent.mkdir(exist_ok=True)
        if not target.exists():
            target.write_text(content, encoding="utf-8")
            created["files"].append(fpath)

    # Create script stubs
    for script_name in structure["scripts"]:
        script_path = skill_dir / "scripts" / script_name
        if not script_path.exists():
            script_path.write_text(f'#!/usr/bin/env python3\n"""TODO: Implement {script_name}"""\n\nimport sys\n\nif __name__ == "__main__":\n    print("Not yet implemented")\n    sys.exit(1)\n', encoding="utf-8")
            script_path.chmod(0o755)
            created["files"].append(f"scripts/{script_name}")

    return created


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scaffold a new skill")
    parser.add_argument("--name", required=True, help="Skill name (kebab-case)")
    parser.add_argument("--category", required=True, choices=list(CATEGORY_MAP.keys()), help="Skill category")
    parser.add_argument("--output", help="Output directory (default: ~/.claude/skills/<name>)")
    parser.add_argument("--description", default="", help="Skill description")
    parser.add_argument("--triggers", nargs="*", help="Trigger phrases")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    result = scaffold(
        name=args.name,
        category=args.category,
        output=args.output,
        description=args.description,
        triggers=args.triggers,
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        print(f"Scaffolded skill at: {result['dir']}")
        print(f"  Created {len(result['files'])} files, {len(result['dirs'])} dirs")
