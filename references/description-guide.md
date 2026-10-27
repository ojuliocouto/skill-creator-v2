# Description Guide: Como escrever descriptions que trigam corretamente

## Principio Core

A `description` e a unica coisa que o sistema le pra decidir se ativa a skill.
Se a description nao captura a intencao do usuario, a skill nunca e invocada.

## Anatomia de uma boa description

```
[O QUE FAZ] + [PARA QUE SERVE] + [TECNOLOGIAS/APIs] + [KEYWORDS NATURAIS]
```

### Exemplo ruim:
```
"Skill de whatsapp"
```
Problema: muito generico, nao diferencia de outras skills de whatsapp.

### Exemplo bom:
```
"Cria, submete e dispara templates WhatsApp via Meta Cloud API. Cobre criacao de template com variaveis, verificacao de status de aprovacao, disparo para lista de contatos com personalizacao. Triggers: criar template, disparar whatsapp, template meta, checar aprovacao."
```

## Estrategias de Description

### 1. Keyword-Rich
Foca em incluir o maximo de termos relevantes.
- Bom para: skills com muitos sinonimos
- Risco: capturar queries irrelevantes (falsos positivos)

### 2. Intent-Focused
Foca na intencao do usuario, nao nas palavras exatas.
- Bom para: skills com poucos sinonimos mas intencao clara
- Risco: perder queries com vocabulario diferente

### 3. Negative-Aware
Inclui clarificacoes do que a skill NAO faz pra evitar colisao.
- Bom para: skills em dominios concorridos (ex: 3 skills de whatsapp)
- Risco: description fica verbosa

## Checklist de Qualidade

1. **Comprimento:** 100-400 chars (ideal ~200)
2. **Especificidade:** alguem lendo sabe EXATAMENTE o que faz?
3. **Keywords:** inclui termos que usuario usaria naturalmente?
4. **Diferenciacao:** se diferencia de skills similares?
5. **Sem instrucoes:** nao tem "primeiro faca X, depois Y"?
6. **Sem emojis:** description limpa, profissional

## Otimizacao Multi-Path

Ao criar uma skill, gere 3 versoes da description:

1. **Keyword-rich:** maximiza recall (captura mais queries)
2. **Intent-focused:** maximiza precision (menos falsos positivos)
3. **Balanced:** mix das duas estrategias

Teste cada uma com `test_triggers.py` e escolha a com melhor F1 score.

## Tamanho vs Performance

| Tamanho | Precision | Recall | Uso ideal |
|---------|-----------|--------|-----------|
| < 100 chars | Alta | Baixa | Skills muito nichadas |
| 100-200 chars | Alta | Media | Maioria dos casos |
| 200-400 chars | Media | Alta | Skills com muitos sinonimos |
| > 400 chars | Baixa | Alta | Evitar - polui contexto |

## Dicas Finais

- Inclua o slash command na description: "Trigger: /nome-skill"
- Use portugues E ingles se ambos sao usados pelo usuario
- Nao repita o nome da skill na description (ja esta no campo `name`)
- Se a skill usa APIs especificas, nomeie-as (Meta API, Hotmart API, etc.)
