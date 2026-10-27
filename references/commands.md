# Comandos Uteis — Skill Creator V2

## Analisar ecossistema
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/analyze_skills.py --summary
```

## Buscar skills por topico
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/analyze_skills.py --search "TOPICO"
```

## Regenerar padroes (patterns.md)
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/analyze_skills.py --generate-patterns
```

## Checar colisao de description
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/collision_check.py \
  --description "DESCRIPTION" --triggers TRIGGER1 TRIGGER2
```

## Auditar skill
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/audit_skill.py \
  --skill-path ~/.claude/skills/NAME/ --html /tmp/audit.html
```

## Extrair frontmatter de skill existente
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/extract_frontmatter.py \
  ~/.claude/skills/NAME/SKILL.md --json --body
```

## Scaffold nova skill
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/scaffold.py \
  --name "nome-skill" --category "workflow" \
  --description "..." --triggers trigger1 trigger2
```
