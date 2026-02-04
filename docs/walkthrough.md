# Template Syntax Error Fix Walkthrough

## Goal
Fix a syntax error in `templates/listar_empresas.html` caused by a split `{% endif %}` tag.

## Changes

### [listar_empresas.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/empresarios/templates/listar_empresas.html)

- **Fix**: Joined the split `{% endif %}` tag on lines 21-22 into a single line to ensure correct template parsing.

```diff
- placeholder="Busque por uma empresa em específico" {% if nome_empresa %}value="{{nome_empresa}}" {%
- endif %}>
+ placeholder="Busque por uma empresa em específico" {% if nome_empresa %}value="{{nome_empresa}}"{% endif %}>
```

## Verification Results

### Manual Verification
- Verified the file content to ensure the `{% if %}` block is correctly closed with `{% endif %}` on the same line.
