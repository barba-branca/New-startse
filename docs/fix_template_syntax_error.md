# Correção de Erro de Sintaxe em Template Django

**Data:** 03/02/2026
**Arquivo:** `templates/listar_empresas.html`

## Descrição do Problema
O arquivo `listar_empresas.html` apresentava um erro de sintaxe na linha 107 (reportado) devido a um bloco `{% if %}` mal fechado nas linhas 21-22.

A tag `{% endif %}` estava quebrada em uma nova linha, o que não é permitido ou estava causando problemas de parsing no interpretador de templates do Django.

**Código Incorreto:**
```html
<input ... {% if nome_empresa %}value="{{nome_empresa}}" {%
  endif %}>
```

## Solução Aplicada
Unificação da tag `{% if %}` e `{% endif %}` na mesma linha.

**Código Corrigido:**
```html
<input ... {% if nome_empresa %}value="{{nome_empresa}}"{% endif %}>
```

## Verificação
O arquivo foi verificado manualmente para garantir que todos os blocos estão fechados corretamente.
