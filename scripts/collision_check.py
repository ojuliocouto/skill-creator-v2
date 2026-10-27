#!/usr/bin/env python3
"""Detect description/trigger collisions with existing skills."""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_frontmatter import extract_frontmatter


def extract_keywords(text: str, min_len: int = 3) -> set:
    """Extract significant keywords from text."""
    words = set(re.findall(r'\w{' + str(min_len) + r',}', text.lower()))
    # Remove very common words
    stopwords = {
        "para", "como", "esse", "esta", "isso", "quando", "usar", "este",
        "que", "com", "por", "uma", "dos", "das", "the", "and", "for",
        "with", "use", "when", "this", "that", "from", "have", "will",
        "can", "should", "skill", "completa", "completo", "sistema",
        "ferramenta", "tool", "tools", "including", "covers", "based",
    }
    return words - stopwords


def check_collision(new_description: str, new_triggers: list = None, skills_dir: str = None) -> dict:
    """Check if a new skill description collides with existing skills."""
    skills_path = Path(skills_dir) if skills_dir else Path.home() / ".claude" / "skills"
    new_keywords = extract_keywords(new_description)
    new_trigger_set = set(t.lower() for t in (new_triggers or []))

    collisions = []

    for skill_dir in sorted(skills_path.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == "skill-creator-v2":
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        fm = extract_frontmatter(str(skill_md))
        existing_desc = fm.get("description", "")
        existing_triggers = fm.get("triggers", [])
        existing_trigger_set = set(
            t.lower() for t in existing_triggers if isinstance(t, str)
        )
        existing_keywords = extract_keywords(existing_desc)

        # Keyword overlap
        overlap = new_keywords & existing_keywords
        overlap_ratio = len(overlap) / max(len(new_keywords), 1)

        # Trigger overlap
        trigger_overlap = new_trigger_set & existing_trigger_set

        # Substring match in descriptions
        desc_substring = False
        for kw in new_keywords:
            if len(kw) >= 5 and kw in existing_desc.lower():
                desc_substring = True
                break

        severity = "none"
        if trigger_overlap:
            severity = "high"
        elif overlap_ratio > 0.4:
            severity = "high"
        elif overlap_ratio > 0.2:
            severity = "medium"
        elif desc_substring and overlap_ratio > 0.1:
            severity = "low"

        if severity != "none":
            collisions.append({
                "skill": skill_dir.name,
                "severity": severity,
                "keyword_overlap": sorted(overlap)[:10],
                "keyword_overlap_ratio": round(overlap_ratio, 2),
                "trigger_overlap": sorted(trigger_overlap),
                "existing_description_preview": existing_desc[:150] + "..." if len(existing_desc) > 150 else existing_desc,
            })

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    collisions.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return {
        "total_skills_checked": len(list(skills_path.iterdir())),
        "collisions_found": len(collisions),
        "high_severity": sum(1 for c in collisions if c["severity"] == "high"),
        "medium_severity": sum(1 for c in collisions if c["severity"] == "medium"),
        "low_severity": sum(1 for c in collisions if c["severity"] == "low"),
        "collisions": collisions,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check for skill collisions")
    parser.add_argument("--description", required=True, help="New skill description")
    parser.add_argument("--triggers", nargs="*", help="New skill triggers")
    parser.add_argument("--skills-dir", help="Skills directory (default: ~/.claude/skills/)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = check_collision(args.description, args.triggers, args.skills_dir)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Checked {result['total_skills_checked']} skills")
        print(f"Collisions: {result['collisions_found']} (H={result['high_severity']} M={result['medium_severity']} L={result['low_severity']})")
        if result["collisions"]:
            print()
            for c in result["collisions"]:
                icon = {"high": "!!!", "medium": "!!", "low": "!"}[c["severity"]]
                print(f"  [{icon}] {c['skill']} ({c['severity']})")
                if c["trigger_overlap"]:
                    print(f"       Trigger overlap: {', '.join(c['trigger_overlap'])}")
                print(f"       Keyword overlap: {c['keyword_overlap_ratio']*100:.0f}% — {', '.join(c['keyword_overlap'][:5])}")
