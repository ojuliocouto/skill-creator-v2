# Frontmatter Guide: Campos SKILL.md

## Campos Obrigatorios

### `name`
- Kebab-case, minusculo: `minha-skill-nova`
- Mesmo nome do diretorio
- Unico no ecossistema

### `description`
- **O campo mais critico.** E o que o sistema usa pra decidir se ativa a skill.
- Tamanho ideal: 100-400 chars
- Deve incluir: o que faz, para que serve, tecnologias/APIs, tipos de input aceitos
- Deve incluir keywords que o usuario usaria naturalmente
- NAO incluir: instrucoes de como usar (isso vai no body)
- Ver `description-guide.md` para detalhes

## Campos Opcionais (mas recomendados)

### `allowed-tools`
- Lista de tools que a skill precisa
- Minimo: `Read, Write, Edit, Bash, Glob, Grep`
- Adicionar MCPs se necessario: `mcp__magic__21st_magic_component_builder`
- Formato: comma-separated na mesma linha

### `triggers`
- Lista de frases que devem ativar a skill
- Incluir: slash command (`/nome-skill`), frases naturais, sinonimos
- 5-15 triggers e ideal
- Evitar triggers muito genericos ("ajuda", "faz")

### `pairs-with`
- Skills complementares
- Formato:
```yaml
pairs-with:
  - skill: nome-skill
    reason: Por que combina
```

## Exemplos de Frontmatter

### Skill de API
```yaml
---
name: whatsapp-template
description: "Cria, submete e dispara templates WhatsApp via Meta Cloud API. Cobre criacao de template, verificacao de status, disparo para lista de contatos, variaveis dinamicas."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
triggers:
  - criar template whatsapp
  - disparar whatsapp
  - template meta
  - /whatsapp-template
---
```

### Skill de Workflow
```yaml
---
name: construtor-paginas
description: "Skill completa para construir paginas web profissionais. Combina: shadcn/ui, Tailwind CSS, animacoes Framer Motion, glassmorphism. Stacks: React, Next.js, HTML+Tailwind."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, mcp__magic__21st_magic_component_builder
triggers:
  - criar pagina
  - landing page
  - site bonito
  - /construtor-paginas
---
```

### Skill de Analise
```yaml
---
name: marketing-analyst
description: "Expert marketing analytics covering campaign analysis, attribution modeling, ROI measurement, and performance reporting."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
triggers:
  - analisar campanha
  - metricas marketing
  - ROI
  - /marketing-analyst
---
```

## Anti-Patterns

- Description vazia ou < 50 chars
- Triggers iguais a outra skill (colisao)
- Sem allowed-tools (skill nao consegue fazer nada)
- Description com instrucoes de uso (polui o campo)
- Triggers com typos (nunca vao ser ativados)
