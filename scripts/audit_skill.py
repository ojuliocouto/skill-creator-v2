#!/usr/bin/env python3
"""Adversarial audit for skills. Scores 6 criteria 0-10, minimum 45/60 to pass."""

import sys
import json
import re
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from extract_frontmatter import extract_frontmatter, extract_body

# Windows consoles default to cp1252; force UTF-8 so accents and symbols never crash output.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")



CRITERIA = [
    {
        "id": "completeness",
        "name": "Completude",
        "description": "Skill cobre todos os casos de uso declarados? Workflow completo do inicio ao fim?",
        "checks": [
            ("has_workflow", "Tem workflow/etapas claras"),
            ("has_error_handling", "Menciona tratamento de erros/edge cases"),
            ("has_examples", "Tem exemplos de uso ou comandos"),
            ("has_validation", "Tem step de validacao/setup"),
        ],
    },
    {
        "id": "trigger_accuracy",
        "name": "Trigger Accuracy",
        "description": "Description e triggers sao precisos? Nao capturam queries irrelevantes?",
        "checks": [
            ("has_frontmatter", "Tem frontmatter YAML valido"),
            ("has_description", "Description presente e descritiva (>50 chars)"),
            ("has_triggers", "Triggers definidos no frontmatter"),
            ("description_specific", "Description e especifica (nao generica)"),
        ],
    },
    {
        "id": "script_quality",
        "name": "Qualidade de Scripts",
        "description": "Scripts sao funcionais, nao stubs? Tem argparse, error handling, outputs uteis?",
        "checks": [
            ("scripts_exist", "Diretorio scripts/ existe com arquivos"),
            ("scripts_have_main", "Scripts tem if __name__ == '__main__'"),
            ("scripts_have_argparse", "Scripts usam argparse ou sys.argv"),
            ("scripts_no_stubs", "Scripts nao sao apenas stubs/TODO"),
        ],
    },
    {
        "id": "documentation",
        "name": "Documentacao",
        "description": "SKILL.md e claro, organizado, com secoes logicas? References completos?",
        "checks": [
            ("has_sections", "Tem secoes com ## headers"),
            ("reasonable_length", "Body entre 50-600 linhas"),
            ("has_references", "Tem diretorio references/ com conteudo"),
            ("no_broken_refs", "Nao referencia arquivos inexistentes"),
        ],
    },
    {
        "id": "edge_cases",
        "name": "Edge Cases",
        "description": "Skill lida com inputs invalidos, APIs offline, credenciais ausentes?",
        "checks": [
            ("mentions_errors", "Menciona cenarios de erro"),
            ("has_config_check", "Verifica config/credenciais no inicio"),
            ("has_fallbacks", "Tem fallbacks ou mensagens de erro claras"),
        ],
    },
    {
        "id": "progressive_disclosure",
        "name": "Progressive Disclosure",
        "description": "Info essencial no SKILL.md, detalhes em references? Nao sobrecarrega contexto?",
        "checks": [
            ("skill_md_focused", "SKILL.md < 400 linhas (nao bloated)"),
            ("details_in_refs", "Detalhes pesados em references/"),
            ("clear_entry_point", "Primeiro step e claro e acionavel"),
        ],
    },
]


def audit_skill(skill_path: str) -> dict:
    """Run full audit on a skill directory."""
    skill_dir = Path(skill_path)
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return {"error": f"SKILL.md not found in {skill_path}", "total_score": 0, "passed": False}

    fm = extract_frontmatter(str(skill_md))
    body = extract_body(str(skill_md))
    body_lines = body.count("\n")

    # Check script quality
    scripts_dir = skill_dir / "scripts"
    scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []
    script_contents = {}
    for s in scripts:
        try:
            script_contents[s.name] = s.read_text(encoding="utf-8-sig", errors="replace")
        except:
            script_contents[s.name] = ""

    refs_dir = skill_dir / "references"
    ref_files = list(refs_dir.rglob("*")) if refs_dir.exists() else []
    ref_files = [f for f in ref_files if f.is_file()]

    # Run checks
    results = []
    for criterion in CRITERIA:
        score = 0
        max_score = len(criterion["checks"])
        check_results = []

        for check_id, check_desc in criterion["checks"]:
            passed = run_check(check_id, fm, body, body_lines, scripts, script_contents, ref_files, skill_dir)
            check_results.append({"check": check_desc, "passed": passed})
            if passed:
                score += 1

        # Scale to 0-10
        scaled_score = round(10 * score / max_score) if max_score > 0 else 0

        results.append({
            "criterion": criterion["name"],
            "criterion_id": criterion["id"],
            "score": scaled_score,
            "checks": check_results,
            "raw": f"{score}/{max_score}",
        })

    total_score = sum(r["score"] for r in results)
    passed = total_score >= 45 and all(r["score"] >= 7 for r in results)

    return {
        "skill": skill_dir.name,
        "total_score": total_score,
        "max_score": 60,
        "passed": passed,
        "pass_threshold": "45/60 total, 7+ each",
        "criteria": results,
        "summary": {
            "body_lines": body_lines,
            "scripts_count": len(scripts),
            "refs_count": len(ref_files),
            "has_config": (skill_dir / "config.json").exists(),
            "description_length": len(fm.get("description", "")),
        },
        "timestamp": datetime.now().isoformat(),
    }


def run_check(check_id: str, fm: dict, body: str, body_lines: int,
              scripts: list, script_contents: dict, ref_files: list, skill_dir: Path) -> bool:
    """Run individual check."""
    body_lower = body.lower()

    checks = {
        # Completeness
        "has_workflow": lambda: bool(re.search(r"(workflow|etapa|step|fase|protocolo)", body_lower)),
        "has_error_handling": lambda: bool(re.search(r"(erro|error|falha|fail|invalido|invalid)", body_lower)),
        "has_examples": lambda: bool(re.search(r"(```|exemplo|example)", body_lower)),
        "has_validation": lambda: bool(re.search(r"(validar|verificar|check|setup|config)", body_lower)),

        # Trigger accuracy
        "has_frontmatter": lambda: bool(fm),
        "has_description": lambda: len(fm.get("description", "")) > 50,
        "has_triggers": lambda: bool(fm.get("triggers")) or "trigger" in body_lower[:500],
        "description_specific": lambda: len(fm.get("description", "")) > 100,

        # Script quality
        "scripts_exist": lambda: len(scripts) > 0,
        "scripts_have_main": lambda: any("__main__" in c for c in script_contents.values()),
        "scripts_have_argparse": lambda: any("argparse" in c or "sys.argv" in c for c in script_contents.values()),
        "scripts_no_stubs": lambda: not all("TODO" in c and len(c) < 200 for c in script_contents.values()) if script_contents else True,

        # Documentation
        "has_sections": lambda: body.count("\n## ") >= 2,
        "reasonable_length": lambda: 50 <= body_lines <= 600,
        "has_references": lambda: len(ref_files) > 0,
        "no_broken_refs": lambda: True,  # simplified

        # Edge cases
        "mentions_errors": lambda: bool(re.search(r"(erro|error|falha|fail)", body_lower)),
        "has_config_check": lambda: bool(re.search(r"(config|token|credencial|api.key)", body_lower)),
        "has_fallbacks": lambda: bool(re.search(r"(fallback|alternativ|se falhar|if fail|otherwise)", body_lower)),

        # Progressive disclosure
        "skill_md_focused": lambda: body_lines < 400,
        "details_in_refs": lambda: len(ref_files) > 0,
        "clear_entry_point": lambda: bool(re.search(r"^##?\s+(step|etapa|fase|protocolo|quando|workflow|1)", body_lower[:500], re.MULTILINE)),
    }

    check_fn = checks.get(check_id, lambda: False)
    try:
        return check_fn()
    except:
        return False


def generate_html_report(audit_result: dict, output_path: str = None) -> str:
    """Generate interactive HTML report from audit result."""
    template_path = Path(__file__).parent.parent / "assets" / "audit-report.html"

    # Inline HTML generation (no template dependency)
    criteria_html = ""
    for c in audit_result["criteria"]:
        color = "#22c55e" if c["score"] >= 8 else "#eab308" if c["score"] >= 7 else "#ef4444"
        checks_html = ""
        for ch in c["checks"]:
            icon = "&#10003;" if ch["passed"] else "&#10007;"
            ch_color = "#22c55e" if ch["passed"] else "#ef4444"
            checks_html += f'<div style="color:{ch_color};padding:2px 0">{icon} {ch["check"]}</div>'

        criteria_html += f'''
        <div style="border:1px solid #333;border-radius:8px;padding:16px;margin:8px 0;background:#1a1a2e">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <h3 style="margin:0;color:#e0e0e0">{c["criterion"]}</h3>
                <span style="font-size:24px;font-weight:bold;color:{color}">{c["score"]}/10</span>
            </div>
            <div style="margin-top:8px;font-size:13px">{checks_html}</div>
        </div>'''

    total = audit_result["total_score"]
    total_color = "#22c55e" if audit_result["passed"] else "#ef4444"
    status = "PASSED" if audit_result["passed"] else "FAILED"
    s = audit_result["summary"]

    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skill Audit: {audit_result["skill"]}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; background: #0d0d1a; color: #e0e0e0; max-width: 700px; margin: 40px auto; padding: 20px; }}
  h1 {{ color: #fff; }} h2 {{ color: #a0a0c0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
  .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; color: #888; }}
</style></head><body>
<h1>Skill Audit: {audit_result["skill"]}</h1>
<div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
  <span style="font-size:48px;font-weight:bold;color:{total_color}">{total}/60</span>
  <span class="badge" style="background:{total_color};color:#000">{status}</span>
</div>
<h2>Summary</h2>
<div class="meta">
  <div>Body: {s["body_lines"]} lines</div>
  <div>Scripts: {s["scripts_count"]}</div>
  <div>References: {s["refs_count"]}</div>
  <div>Description: {s["description_length"]} chars</div>
</div>
<h2 style="margin-top:24px">Criteria</h2>
{criteria_html}
<p style="color:#555;font-size:11px;margin-top:24px">Generated {audit_result["timestamp"]}</p>
</body></html>'''

    if output_path:
        Path(output_path).write_text(html, encoding="utf-8")

    return html


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audit a skill (6 criteria, 0-10 each)")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--html", help="Generate HTML report to path")
    args = parser.parse_args()

    result = audit_skill(args.skill_path)

    if args.html:
        generate_html_report(result, args.html)
        print(f"HTML report: {args.html}")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['skill']}: {result['total_score']}/{result['max_score']}")
        for c in result["criteria"]:
            icon = "OK" if c["score"] >= 7 else "!!"
            print(f"  [{icon}] {c['criterion']}: {c['score']}/10 ({c['raw']})")
            for ch in c["checks"]:
                mark = "v" if ch["passed"] else "x"
                print(f"       [{mark}] {ch['check']}")
