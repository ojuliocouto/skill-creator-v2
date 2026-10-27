---
name: skill-creator-v2
description: "Cria skills profissionais com pesquisa automatica, templates por categoria (API/workflow/analysis/creative/utility), collision detection contra skills existentes, auditoria adversarial (6 criterios, minimo 45/60), scaffolding automatico com codigo funcional. Modos: criar skill nova, clonar skill existente, melhorar skill existente. Supera o skill-creator da Anthropic em pesquisa, templates, collision detection e auditoria."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Agent
triggers:
  - criar skill
  - nova skill
  - /skill-creator-v2
  - criar uma skill de
  - skill para
  - montar skill
  - gerar skill
  - clonar skill
  - melhorar skill
  - melhorar minha skill
  - skill que faz
  - skill creator
  - build skill
pairs-with:
  - skill: find-skills
    reason: Descobrir skills existentes antes de criar novas
---

# Skill Creator V2: Criador de Skills Profissionais

Cria skills melhores que o skill-creator da Anthropic. Pesquisa antes de escrever, usa templates por categoria, detecta colisao com skills existentes e audita com 6 criterios antes de entregar.

---

## PRÉ-REQUISITO: PYTHON (macOS, Linux e Windows)

Os comandos desta skill usam `python3` e caminhos com `~`. Funcionam iguais nos 3 sistemas, porque o Claude Code no Windows roda os comandos no Git Bash.

1. Rodar `python3 --version`.
2. Se falhar ou abrir a Microsoft Store (Windows), rodar `py -3 --version`, depois `python --version`.
3. Usar o primeiro que responder Python 3.9 ou mais novo no lugar de `python3` em todos os comandos abaixo.
4. Se nenhum responder: parar e pedir para instalar o Python 3 (python.org; no Windows, marcar "Add python.exe to PATH").

---

## DETECTAR MODO

| Modo | Trigger | Descricao |
|------|---------|-----------|
| **CREATE** | "cria uma skill de X" | Nova skill do zero |
| **CLONE** | "faz uma skill igual a X mas pra Y" | Copia estrutura, adapta dominio |
| **IMPROVE** | "melhora minha skill X" | Audita, identifica fraquezas, corrige |

---

## MODO CREATE: 6 Fases

### FASE 1: Research

**1.1 Perguntas Clarificadoras (3-5)**
- Qual o **publico-alvo**? (tecnico, leigo, misto)
- Quais **casos de uso** principais? (3-5 cenarios)
- Quais **ferramentas/APIs** a skill usa?
- Tem **credenciais** necessarias?
- Existe skill similar que deveria ser complementar?

**1.2 Auto-Research**
Pesquisar: docs das APIs (WebSearch/WebFetch), bibliotecas Python relevantes, best practices.

**1.3 Checar Skills Similares**
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/analyze_skills.py --search "TOPICO"
```
Se similar existir: perguntar se (a) criar separada, (b) melhorar existente, (c) criar como complementar.

**1.4 Determinar Categoria**
- **api-integration**: APIs externas (WhatsApp, ManyChat, Notion)
- **workflow**: multiplas fases (construtor-paginas, deploy)
- **analysis**: analise e relatorios (marketing-analyst, funnel)
- **creative**: geracao de conteudo (criativo-imagem-ia, video)
- **utility**: ferramentas standalone (ffmpeg, scraping)

**1.5 Resumo para Aprovacao**
```
Topico: X | Categoria: Y | APIs: [...] | Skills similares: [...] | Plano: breve
Aprovar?
```

---

### FASE 2: Arquitetura

**2.1 Template**
```bash
cat ~/.claude/skills/skill-creator-v2/references/templates/{CATEGORY}.md
```

**2.2 Estrutura + Frontmatter**
Planejar: scripts necessarios, reference files, se precisa config.json.
Consultar guia: `cat ~/.claude/skills/skill-creator-v2/references/frontmatter-guide.md`

**2.3 Apresentar e Aprovar**
```
~/.claude/skills/{name}/
├── SKILL.md
├── scripts/
├── references/
└── config.json (se precisar)

name: ... | description: "..." | triggers: [...]
Aprovar?
```

---

### FASE 3: Build

**3.1 Scaffold**
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/scaffold.py \
  --name "{NAME}" --category "{CATEGORY}" \
  --description "{DESCRIPTION}" --triggers {T1} {T2} {T3}
```

**3.2 Escrever SKILL.md**
- Template da categoria como base
- Padroes: `cat ~/.claude/skills/skill-creator-v2/references/patterns.md`
- Writing guide: `cat ~/.claude/skills/skill-creator-v2/references/writing-guide.md`
- OBRIGATORIO: body < 400 linhas | comandos reais | checkpoints de validacao | config check se precisar de credenciais

**3.3 Escrever Scripts**
- Codigo funcional com argparse + `if __name__ == "__main__"`
- Error handling | stdlib Python 3 only | chmod +x

**3.4 Escrever References**
Detalhes que nao cabem no SKILL.md: payloads de API, exemplos longos, benchmarks.

---

### FASE 4: Description + Collision Check

**4.1 Escrever Description**
Consultar: `cat ~/.claude/skills/skill-creator-v2/references/description-guide.md`

Regras essenciais: 100-400 chars | especifica | keywords naturais | sem instrucoes de uso.

**4.2 Collision Check**
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/collision_check.py \
  --description "DESCRIPTION_FINAL" --triggers {TRIGGERS}
```
- HIGH severity: ajustar description ou triggers antes de continuar
- MEDIUM: reportar ao usuario e perguntar

**4.3 Reportar**
```
Collisions: N (H=H M=M L=L)
```

---

### FASE 5: Auditoria Adversarial

**5.1 Rodar**
```bash
python3 ~/.claude/skills/skill-creator-v2/scripts/audit_skill.py \
  --skill-path ~/.claude/skills/{NAME}/ \
  --html "$SCRATCHPAD/skill-audit-{NAME}.html"
```

O relatório HTML vai para o scratchpad da sessão (`$SCRATCHPAD` = o diretório de scratchpad da sessão, nunca `/tmp` solto). Não rodar `open`: abrir só se o usuário pedir, e então pelo Edge do Claude em segundo plano (`connect({ novaAba: 'file://...' })` do `~/.claude/scripts/cdp.mjs`), nunca pelo navegador padrão (que pode ser o navegador pessoal do usuário).

**5.2 Criterios (6, 0-10 cada)**
1. **Completude**: workflow completo, error handling, exemplos
2. **Trigger Accuracy**: frontmatter valido, description especifica
3. **Qualidade de Scripts**: funcionais, argparse, nao stubs
4. **Documentacao**: secoes logicas, tamanho adequado, references
5. **Edge Cases**: erros, config check, fallbacks
6. **Progressive Disclosure**: SKILL.md focado, detalhes em refs

**5.3 Minimo:** 7+ em cada criterio individual | 45+ total (de 60)

**5.4 Auto-Fix**
Se reprovar: corrigir criterios < 7 e re-auditar. Maximo 3 tentativas.
Se ainda reprovar na 3a: entregar com aviso explicitando o que falhou.

---

### FASE 6: Entrega

```
Skill: {NAME} | Categoria: {CATEGORY} | ~/.claude/skills/{NAME}/
Auditoria: {SCORE}/60 ({PASS/FAIL})
Collisions: N (H=H M=M L=L)
Pronto: /{NAME}
```

---

## MODO CLONE

Fonte: `~/.claude/skills/{SOURCE}/`

1. Ler SKILL.md + scripts + references da fonte completamente
2. Extrair estrutura: `python3 ~/.claude/skills/skill-creator-v2/scripts/extract_frontmatter.py ~/.claude/skills/{SOURCE}/SKILL.md --json --body`
3. Scaffold com mesma categoria: `scaffold.py --name "{NEW_NAME}" --category "{SAME_CATEGORY}"`
4. Adaptar SKILL.md (trocar dominio/APIs, manter estrutura)
5. Adaptar scripts (copiar estrutura, trocar logica)
6. Executar Fases 4-6

---

## MODO IMPROVE

1. Ler skill: `cat ~/.claude/skills/{NAME}/SKILL.md`
2. Auditar: `audit_skill.py --skill-path ~/.claude/skills/{NAME}/`
3. Identificar criterios < 8 e propor melhorias ao usuario
4. Aplicar melhorias aprovadas
5. Executar Fases 4-6

---

## ANTI-PATTERNS

- NUNCA criar skill sem pesquisa previa (Fase 1 nao e opcional)
- NUNCA pular collision check (2 skills com mesmo trigger = caos)
- NUNCA entregar skill com audit score < 45/60
- NUNCA escrever SKILL.md > 400 linhas (usar references/)
- NUNCA criar scripts stub com TODO (codigo funcional ou nao criar)
- NUNCA hardcodar paths que so funcionam numa maquina
- NUNCA duplicar funcionalidade de skill existente sem justificativa
