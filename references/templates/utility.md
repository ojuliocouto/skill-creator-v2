# {SKILL_NAME}: {UTILITY_DESCRIPTION}

## Visao Geral

Ferramenta para {UTILITY_PURPOSE}. Aceita {INPUT_TYPES}, processa e entrega {OUTPUT_TYPE}.

**Dependencias:** {DEPENDENCIES}

---

## Uso Rapido

```bash
# Comando principal
python3 ~/.claude/skills/{SKILL_DIR}/scripts/{MAIN_SCRIPT} --input {INPUT} --output {OUTPUT}
```

## Opcoes

| Flag | Descricao | Default |
|------|-----------|---------|
| `--input` | {INPUT_DESC} | obrigatorio |
| `--output` | {OUTPUT_DESC} | stdout |
| `--format` | {FORMAT_DESC} | {DEFAULT_FORMAT} |
| `--verbose` | Modo detalhado | false |

---

## Exemplos

### Exemplo 1: {USE_CASE_1}
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/{MAIN_SCRIPT} {EXAMPLE_1}
```

### Exemplo 2: {USE_CASE_2}
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/{MAIN_SCRIPT} {EXAMPLE_2}
```

---

## Edge Cases
- Input invalido: {HANDLING}
- Arquivo grande: {SIZE_LIMITS}
- Encoding: {ENCODING_HANDLING}
