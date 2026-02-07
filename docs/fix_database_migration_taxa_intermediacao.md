# Fix: Erro de Coluna Inexistente (taxa_intermediacao)

## Problema
Ocorreu um erro ao tentar acessar a página de "Ver Empresa" (`investidores/templates/ver_empresa.html`):

```
sqlite3.OperationalError: no such column: empresarios_empresas.taxa_intermediacao
```

## Causa
O modelo `Empresas` em `empresarios/models.py` possuía o campo `taxa_intermediacao` definido, mas a migração correspondente (`0005_empresas_taxa_intermediacao_empresas_valor_liquido.py`) não havia sido aplicada ao banco de dados `db.sqlite3`. Isso causou um descompasso entre a definição do código e o esquema do banco de dados.

## Solução
Foi executado o comando para aplicar as migrações pendentes:

```bash
python manage.py migrate
```

O Django aplicou a migração `0005`, criando as colunas `taxa_intermediacao` e `valor_liquido` na tabela `empresarios_empresas`.

## Verificação
Após a migração, o acesso à página da empresa foi normalizado, pois o banco de dados agora possui as colunas esperadas pelo Django ORM.

## Como Prevenir
Sempre que houver alterações nos arquivos `models.py` (adicionar/remover campos), certifique-se de:
1. Criar a migração: `python manage.py makemigrations`
2. Aplicar a migração: `python manage.py migrate`
