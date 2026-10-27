#!/usr/bin/env python3
"""Test trigger precision/recall for a skill description.

Tests how well a description matches intended queries (should-trigger)
and rejects unintended queries (should-not-trigger).

Uses Wilson score interval for confidence bounds.
Supports multi-path optimization: test multiple description strategies.
"""

import sys
import json
import re
import math
import subprocess
from pathlib import Path

# Windows consoles default to cp1252; force UTF-8 so accents and symbols never crash output.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")



def wilson_score(successes: int, total: int, z: float = 1.96) -> tuple:
    """Wilson score interval for binomial proportion (95% CI by default)."""
    if total == 0:
        return (0.0, 0.0, 0.0)
    p_hat = successes / total
    denominator = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denominator
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denominator
    lower = max(0, center - spread)
    upper = min(1, center + spread)
    return (lower, p_hat, upper)


def keyword_match(description: str, query: str) -> bool:
    """Simple keyword overlap heuristic for trigger matching."""
    desc_words = set(re.findall(r'\w{3,}', description.lower()))
    query_words = set(re.findall(r'\w{3,}', query.lower()))

    # Direct substring match
    if query.lower() in description.lower():
        return True

    # Significant word overlap
    overlap = desc_words & query_words
    if len(overlap) >= 2:
        return True

    # Check if any query word appears as substring in description
    for qw in query_words:
        if len(qw) >= 4:
            for dw in desc_words:
                if qw in dw or dw in qw:
                    return True

    return False


def evaluate_description(description: str, eval_set: dict) -> dict:
    """Evaluate a description against an eval set of queries."""
    should_trigger = eval_set.get("should_trigger", [])
    should_not_trigger = eval_set.get("should_not_trigger", [])

    tp, fn, tn, fp = 0, 0, 0, 0
    false_negatives = []
    false_positives = []

    for query in should_trigger:
        if keyword_match(description, query):
            tp += 1
        else:
            fn += 1
            false_negatives.append(query)

    for query in should_not_trigger:
        if keyword_match(description, query):
            fp += 1
            false_positives.append(query)
        else:
            tn += 1

    total_pos = tp + fn
    total_neg = tn + fp
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    precision_ci = wilson_score(tp, tp + fp)
    recall_ci = wilson_score(tp, tp + fn)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp, "fn": fn, "tn": tn, "fp": fp,
        "precision_ci_95": {"lower": precision_ci[0], "point": precision_ci[1], "upper": precision_ci[2]},
        "recall_ci_95": {"lower": recall_ci[0], "point": recall_ci[1], "upper": recall_ci[2]},
        "false_negatives": false_negatives,
        "false_positives": false_positives,
    }


def generate_eval_set(skill_name: str, skill_topic: str, triggers: list = None) -> dict:
    """Generate a default eval set based on skill name and topic."""
    # Base should-trigger from triggers
    should_trigger = list(triggers or [])

    # Add variations
    topic_words = skill_topic.lower().split()
    if skill_name:
        should_trigger.append(f"/{skill_name}")
        should_trigger.append(f"usar {skill_name}")
        should_trigger.append(skill_name.replace("-", " "))

    # Generic should-not-trigger
    should_not_trigger = [
        "bom dia",
        "qual hora",
        "me ajuda com git",
        "faz um commit",
        "qual meu saldo",
        "traduz isso pra ingles",
        "cria um dockerfile",
        "configura nginx",
        "explica kubernetes",
        "faz um select no banco",
        "monta um cron job",
        "qual o clima hoje",
        "abre o spotify",
        "faz backup do mongo",
        "instala o node",
    ]

    return {
        "should_trigger": should_trigger[:15],
        "should_not_trigger": should_not_trigger[:15],
    }


def multi_path_optimize(descriptions: list, eval_set: dict) -> list:
    """Evaluate multiple description strategies and rank them."""
    results = []
    for i, desc in enumerate(descriptions):
        result = evaluate_description(desc, eval_set)
        result["strategy_index"] = i
        result["description_preview"] = desc[:100] + "..." if len(desc) > 100 else desc
        results.append(result)

    return sorted(results, key=lambda x: x["f1"], reverse=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test trigger precision/recall")
    parser.add_argument("--description", help="Description to test")
    parser.add_argument("--descriptions", nargs="*", help="Multiple descriptions for multi-path")
    parser.add_argument("--eval-set", help="Path to eval set JSON file")
    parser.add_argument("--skill-name", help="Skill name for auto-generating eval set")
    parser.add_argument("--skill-topic", help="Skill topic for auto-generating eval set")
    parser.add_argument("--triggers", nargs="*", help="Known triggers for eval set generation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Load or generate eval set
    if args.eval_set:
        eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8-sig"))
    elif args.skill_name or args.skill_topic:
        eval_set = generate_eval_set(
            args.skill_name or "",
            args.skill_topic or "",
            args.triggers,
        )
    else:
        print("Error: provide --eval-set or --skill-name/--skill-topic", file=sys.stderr)
        sys.exit(1)

    # Multi-path mode
    if args.descriptions:
        results = multi_path_optimize(args.descriptions, eval_set)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for i, r in enumerate(results):
                print(f"\n--- Strategy #{r['strategy_index']+1} (F1={r['f1']:.2f}) ---")
                print(f"  Precision: {r['precision']:.2f} [{r['precision_ci_95']['lower']:.2f}-{r['precision_ci_95']['upper']:.2f}]")
                print(f"  Recall:    {r['recall']:.2f} [{r['recall_ci_95']['lower']:.2f}-{r['recall_ci_95']['upper']:.2f}]")
                if r["false_negatives"]:
                    print(f"  Missed: {r['false_negatives']}")
                if r["false_positives"]:
                    print(f"  False triggers: {r['false_positives']}")
        sys.exit(0)

    # Single description mode
    if args.description:
        result = evaluate_description(args.description, eval_set)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Precision: {result['precision']:.2f} [{result['precision_ci_95']['lower']:.2f}-{result['precision_ci_95']['upper']:.2f}]")
            print(f"Recall:    {result['recall']:.2f} [{result['recall_ci_95']['lower']:.2f}-{result['recall_ci_95']['upper']:.2f}]")
            print(f"F1:        {result['f1']:.2f}")
            print(f"TP={result['tp']} FN={result['fn']} TN={result['tn']} FP={result['fp']}")
            if result["false_negatives"]:
                print(f"\nMissed queries:")
                for fn in result["false_negatives"]:
                    print(f"  - {fn}")
            if result["false_positives"]:
                print(f"\nFalse triggers:")
                for fp in result["false_positives"]:
                    print(f"  - {fp}")
    else:
        print("Error: provide --description or --descriptions", file=sys.stderr)
        sys.exit(1)
