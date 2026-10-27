# {SKILL_NAME}: {ANALYSIS_DOMAIN}

## Visao Geral

Skill de analise para {DOMAIN}. Coleta dados, processa metricas e gera relatorios acionaveis.

**Stack:**
- Dados: {DATA_SOURCES}
- Processamento: Python 3 stdlib
- Output: {OUTPUT_FORMAT} (JSON, HTML report, markdown)

---

## STEP 1: Coleta de Dados

### 1.1 Fonte de Dados
{DATA_SOURCE_INSTRUCTIONS}

### 1.2 Validacao dos Dados
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/analyze.py --validate --input {INPUT}
```

**Checkpoint:** Dados carregados, {N} registros encontrados.

---

## STEP 2: Analise

### 2.1 Metricas Principais
- {METRIC_1}: {DEFINITION}
- {METRIC_2}: {DEFINITION}
- {METRIC_3}: {DEFINITION}

### 2.2 Execucao
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/analyze.py --input {INPUT} --output /tmp/analysis.json
```

---

## STEP 3: Relatorio

### 3.1 Gerar Relatorio
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/report.py --input /tmp/analysis.json --output /tmp/report.html
```

### 3.2 Insights
Apresentar ao usuario:
1. Top 3 insights acionaveis
2. Metricas com anomalias
3. Recomendacoes priorizadas

---

## Benchmarks de Referencia

| Metrica | Ruim | Medio | Bom | Excelente |
|---------|------|-------|-----|-----------|
| {METRIC_1} | {V1} | {V2} | {V3} | {V4} |
| {METRIC_2} | {V1} | {V2} | {V3} | {V4} |

---

## Edge Cases
- Dados insuficientes: minimo {MIN_RECORDS} registros
- Outliers: {OUTLIER_HANDLING}
- Dados faltantes: {MISSING_DATA_HANDLING}
