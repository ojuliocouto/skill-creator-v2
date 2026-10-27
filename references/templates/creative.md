# {SKILL_NAME}: {CREATIVE_DOMAIN}

## Visao Geral

Sistema de geracao de {OUTPUT_TYPE}. Transforma {INPUT_TYPE} em {OUTPUT_DESCRIPTION}.

**Stack:**
- Geracao: {AI_MODEL} via {PROVIDER} (~${COST}/unidade)
- Processamento: {PROCESSING_TOOL}
- Entrega: {DELIVERY_FORMAT}

---

## STEP 1: Validacao do Setup

### 1.1 Verificar Config
```bash
cat ~/.claude/skills/{SKILL_DIR}/config.json
```

Se token vazio:
> Token nao configurado. Acesse {TOKEN_URL} e gere um token.

### 1.2 Testar Conexao
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/generate.py --test
```

---

## STEP 2: Coleta de Inputs

### 2.1 Input Principal (OBRIGATORIO)
- {INPUT_1_DESCRIPTION}
- Formatos aceitos: {FORMATS}

### 2.2 Referencias Visuais (opcional)
- {REFERENCE_INSTRUCTIONS}

### 2.3 Parametros
- Estilo: {STYLES}
- Formato: {DIMENSIONS}
- Quantidade: {MIN}-{MAX}

---

## STEP 3: Geracao

### 3.1 Modo Single
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/generate.py \
  --input {INPUT} \
  --style {STYLE} \
  --output /tmp/{OUTPUT_DIR}/
```

### 3.2 Modo Batch
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/generate.py \
  --batch {BATCH_CONFIG} \
  --workers {N_WORKERS} \
  --output /tmp/{OUTPUT_DIR}/
```

**Checkpoint:** {N} arquivos gerados em /tmp/{OUTPUT_DIR}/

---

## STEP 4: Auditoria de Qualidade

### 4.1 Criterios
- {CRITERION_1}: {THRESHOLD}
- {CRITERION_2}: {THRESHOLD}
- {CRITERION_3}: {THRESHOLD}

### 4.2 Score Minimo: {MIN_SCORE}/{MAX_SCORE}
Se reprovar: regenerar com parametros ajustados (max 3 tentativas).

---

## STEP 5: Entrega

### 5.1 Report
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/report.py --dir /tmp/{OUTPUT_DIR}/ --output /tmp/report.html
```

### 5.2 Abrir no browser
```bash
open /tmp/report.html
```

---

## Edge Cases
- API offline: {FALLBACK}
- Input de baixa qualidade: {HANDLING}
- Custo alto: {COST_CONTROLS}
