# skill-creator-v2

A [Claude Code](https://claude.com/claude-code) skill that creates, clones and improves other Claude Code skills. It researches the domain before writing, starts from a template per skill category, checks the new skill against every installed skill for trigger collisions, and runs an adversarial audit (6 criteria, minimum 45 of 60) before delivery.

The skill body is in Portuguese. It also carries 2 conventions from the author's own setup (session scratchpad, a dedicated debugging browser). Read the "Author-specific conventions" section before you use it.

## What this is, and what it is not

**It is:**

- A **3-mode workflow** in `SKILL.md` (215 lines):
  - **CREATE**: 6 phases. Research, architecture, build, description plus collision check, adversarial audit, delivery.
  - **CLONE**: copies the structure of an installed skill and adapts it to a new domain.
  - **IMPROVE**: audits an installed skill, proposes fixes for every criterion under 8, applies the approved ones.
- **5 category templates** in `references/templates/`: `api-integration`, `workflow`, `analysis`, `creative`, `utility`.
- **4 writing guides** in `references/`: frontmatter, description, writing style and recurring patterns, plus a command cheat sheet. `patterns.md` ships with aggregate statistics only. `analyze_skills.py --generate-patterns` rewrites it with the catalog of your own installed skills.
- **6 working Python scripts** in `scripts/` (stdlib only, no `pip install`).
- **One HTML audit report template** in `assets/audit-report.html`.

**It is not:**

- A skill marketplace or installer. To find and install published skills, use `find-skills`.
- An eval runner. The audit is a static check of structure and content. It does not run the new skill against test prompts and it does not measure pass rates.
- A replacement for reading the skill it creates. A score of 45/60 means the structure is sound. It does not mean the domain content is correct.

## How it works

1. Claude Code loads `SKILL.md` when the user asks to create, clone or improve a skill ("cria uma skill de X", "melhora minha skill Y", `/skill-creator-v2`).
2. The skill detects the mode from the request.
3. In CREATE mode it asks 3 to 5 clarifying questions, researches the APIs and libraries, and runs `analyze_skills.py --search` to find similar installed skills.
4. It picks a category, reads the matching template and asks for approval of the structure and frontmatter.
5. `scaffold.py` creates the folder, `SKILL.md`, `scripts/` and `references/`. Claude then writes the real content.
6. `collision_check.py` compares the new description and triggers with every installed skill. A HIGH collision blocks delivery until the description or triggers change.
7. `audit_skill.py` scores 6 criteria from 0 to 10. The skill passes with 7 or more on each criterion and 45 or more in total. On a fail, Claude fixes the weak criteria and audits again, up to 3 attempts.

## Scripts

| Script | What it does |
|---|---|
| `analyze_skills.py` | Lists and searches installed skills (`--search "topic"`). |
| `collision_check.py` | Scores trigger and description overlap between a draft and installed skills. |
| `scaffold.py` | Creates the folder and files of a new skill from a category template. |
| `audit_skill.py` | Runs the 6-criterion audit and writes an optional HTML report (`--html <file>`). |
| `extract_frontmatter.py` | Prints the frontmatter (and optionally the body) of a `SKILL.md` as JSON. |
| `test_triggers.py` | Measures trigger precision and recall of a description against should-trigger and should-not-trigger queries, with Wilson score confidence bounds. |

## Audit criteria

| # | Criterion | What it checks |
|---|---|---|
| 1 | Completeness | Full workflow, error handling, examples. |
| 2 | Trigger accuracy | Valid frontmatter, specific description. |
| 3 | Script quality | Working scripts with argparse, no stubs. |
| 4 | Documentation | Logical sections, adequate size, references. |
| 5 | Edge cases | Errors, config check, fallbacks. |
| 6 | Progressive disclosure | Focused `SKILL.md`, detail moved to `references/`. |

Self-audit of this skill on 2026-10-27: **57/60 (PASS)**. The 3 lost points are in progressive disclosure: the audit does not find a clear, actionable first step.

## Onboarding and prerequisites

Before installing, make sure you have:

- **Claude Code** (CLI, desktop app or IDE extension).
- **Python 3.8 or later** on the `PATH` as `python3`. The scripts use the standard library only.
- **No credentials, no API key, no account.** The skill only reads and writes local files. Phase 1 uses Claude Code's own WebSearch and WebFetch tools for research.

## Installation

```bash
git clone https://github.com/ojuliocouto/skill-creator-v2.git ~/.claude/skills/skill-creator-v2
```

Restart Claude Code or open a new session. The skill must live at exactly `~/.claude/skills/skill-creator-v2/`, because `SKILL.md` calls its scripts and templates by that absolute path.

To verify the install:

```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/audit_skill.py --skill-path ~/.claude/skills/skill-creator-v2/
```

The last line must read `[PASS]` with a score of 45/60 or more.

## Author-specific conventions

Phase 5 contains 2 rules from the author's setup:

- The HTML audit report goes to `$SCRATCHPAD`, the Claude Code session scratchpad directory, and never to a loose `/tmp` path.
- The report is not opened automatically. If the user asks to see it, it opens in a dedicated debugging browser through `~/.claude/scripts/cdp.mjs`, which is not part of this repository.

On another machine, replace `$SCRATCHPAD` with any writable directory and open the report with any browser.

## Repository layout

```
skill-creator-v2/
├── SKILL.md
├── README.md
├── LICENSE
├── assets/audit-report.html
├── references/
│   ├── commands.md
│   ├── description-guide.md
│   ├── frontmatter-guide.md
│   ├── patterns.md
│   ├── writing-guide.md
│   └── templates/ (analysis, api-integration, creative, utility, workflow)
└── scripts/ (6 Python scripts)
```

## Security

The repository contains no token, key, password or infrastructure ID. The scripts make no network calls. Before every push, the author's global pre-push hook scans the commits for secrets.

## License

MIT. See `LICENSE`.
