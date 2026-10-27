# {SKILL_NAME}: {API_NAME} Integration

## Visao Geral

Skill para interagir com a API {API_NAME}. Cobre: autenticacao, endpoints principais, tratamento de erros e rate limiting.

**Stack:**
- API: {API_NAME} {API_VERSION}
- Auth: {AUTH_METHOD} (token em config.json)
- Scripts: Python 3 stdlib (urllib, json)

---

## STEP 1: Validacao do Setup

### 1.1 Verificar Config
```bash
cat ~/.claude/skills/{SKILL_DIR}/config.json
```

Campos obrigatorios:
- `api_token`: Token de autenticacao
- `base_url`: URL base da API

Se token vazio:
> Token nao configurado. Acesse {TOKEN_URL} e gere um token.

### 1.2 Testar Conexao
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/api_client.py --test
```

---

## STEP 2: Operacoes Principais

### 2.1 {OPERATION_1}
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/api_client.py --action {ACTION_1} --params '{}'
```

### 2.2 {OPERATION_2}
```bash
python3 ~/.claude/skills/{SKILL_DIR}/scripts/api_client.py --action {ACTION_2} --params '{}'
```

---

## STEP 3: Validacao

**Checkpoint:** Verificar resposta da API:
```bash
python3 -c "import json; print(json.dumps(json.load(open('/tmp/api_response.json')), indent=2))"
```

---

## Edge Cases

### Rate Limiting
- API retorna 429: esperar {RATE_LIMIT_SECONDS}s e retentar
- Maximo de {MAX_RETRIES} retentativas

### Token Expirado
- API retorna 401: renovar token em config.json
- Se OAuth: rodar flow de refresh

### Payload Invalido
- API retorna 400: verificar campos obrigatorios
- Consultar `references/api-payloads.md` para formato correto

---

## References
- Payloads: `references/api-payloads.md`
- Documentacao oficial: {API_DOCS_URL}
