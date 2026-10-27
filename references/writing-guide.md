# Writing Guide: Best Practices para SKILL.md

## Estrutura Recomendada

```markdown
---
(frontmatter)
---

# Nome da Skill: Subtitulo

## Visao Geral
(1-3 paragrafos: o que faz, stack, por que existe)

## STEP 1: Validacao / Setup
(verificar config, credenciais, dependencias)

## STEP 2: Coleta de Inputs
(o que o usuario precisa fornecer)

## STEP 3: Execucao
(workflow principal, comandos, scripts)

## STEP 4: Validacao de Output
(como verificar que funcionou)

## STEP 5: Entrega
(output final pro usuario)

## Edge Cases / Troubleshooting
(erros comuns e como resolver)

## Anti-Patterns
(o que NAO fazer)
```

## Regras de Escrita

### 1. Progressive Disclosure
- SKILL.md = instrucoes essenciais (max 400 linhas)
- Detalhes pesados → `references/`
- Exemplos longos → `references/examples/`
- Payloads de API → `references/api-payloads.md`

### 2. Comandos Reais, Nao Stubs
```bash
# BOM: comando funcional
python3 ~/.claude/skills/minha-skill/scripts/analyze.py --input "$FILE" --output /tmp/result.json

# RUIM: stub que nao faz nada
# TODO: implementar analise
```

### 3. Checkpoints de Validacao
Apos cada step critico, incluir validacao:
```markdown
**Checkpoint:** Verificar que o output existe e tem conteudo:
\`\`\`bash
ls -la /tmp/output.json && python3 -c "import json; d=json.load(open('/tmp/output.json')); print(f'{len(d)} items')"
\`\`\`
```

### 4. Config Pattern
Se a skill precisa de credenciais:
```markdown
## Config
Config em: `~/.claude/skills/nome/config.json`

Carregar no inicio:
\`\`\`bash
cat ~/.claude/skills/nome/config.json
\`\`\`

Se token vazio:
> Token nao configurado. Acesse [URL] e gere um token.
```

### 5. Error Handling Explicito
```markdown
### Se der erro X
1. Verificar Y
2. Tentar Z
3. Se persistir: [acao alternativa]
```

## Tamanho Ideal por Categoria

| Categoria | SKILL.md | references/ |
|-----------|----------|-------------|
| API Integration | 150-250 linhas | 2-4 files (payloads, auth, examples) |
| Workflow | 200-350 linhas | 3-6 files (templates, patterns, sessions) |
| Analysis | 100-200 linhas | 2-3 files (metrics, benchmarks) |
| Creative | 150-300 linhas | 2-4 files (prompts, styles, assets) |
| Utility | 80-150 linhas | 1-2 files (examples) |

## Padroes de Linguagem

- Imperativo: "Verificar config", "Rodar script", "Validar output"
- Sem ambiguidade: "SEMPRE fazer X antes de Y"
- Marcadores de obrigatoriedade: OBRIGATORIO, NUNCA, SEMPRE (caps)
- Sem rodeios: ir direto ao ponto
- Codigo inline com backticks: `nome_variavel`, `/caminho/arquivo`

## Anti-Patterns de Escrita

- Body > 400 linhas (tudo devia ir pra references)
- Repetir a description no corpo
- Instrucoes vagas ("configure adequadamente")
- Falta de exemplos de uso
- Scripts referenciados que nao existem
- Hardcoded paths que so funcionam na maquina do autor
- Secoes vazias com "TODO"
