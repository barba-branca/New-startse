# Migração para PostgreSQL e Deploy no Azure

Este documento descreve os passos necessários para configurar a aplicação para usar PostgreSQL, especialmente em ambiente de produção (Azure).

## Motivação
O uso do SQLite em produção (Azure App Service) causa problemas de persistência e sincronização de schema (`sqlite3.OperationalError: no such column`), pois o sistema de arquivos pode ser efêmero ou não persistir correta e atomicamente entre deploys/restarts. O PostgreSQL é o banco de dados recomendado para produção.

## Alterações Realizadas

1.  **Dependências**: Adicionada a biblioteca `dj-database-url` e `psycopg2-binary` (já existente) no `requirements.txt`.
2.  **Configuração (`settings.py`)**:
    O `settings.py` foi alterado para usar `dj_database_url` para ler a configuração do banco de dados a partir da variável de ambiente `DATABASE_URL`.

    ```python
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
            conn_max_age=600,
            ssl_require=False 
        )
    }
    ```
    Isso mantém o SQLite como fallback para desenvolvimento local caso a variável não esteja definida.

3.  **Ambiente (`.env`)**:
    Adicionado suporte/exemplo para `DATABASE_URL`.

## Instruções de Configuração (Obrigatório para Produção)

Para que a aplicação funcione corretamente no Azure e execute as migrações (criando as tabelas e colunas necessárias), você deve configurar a variável de ambiente `DATABASE_URL`.

### No Azure App Service:

1.  Acesse o **Azure Portal**.
2.  Vá para o seu **App Service**.
3.  No menu lateral, clique em **Settings** > **Environment variables**.
4.  Adicione uma nova variável:
    *   **Name**: `DATABASE_URL`
    *   **Value**: `postgres://usuario:senha@host:porta/nome_do_banco`
        *   Exemplo: `postgres://startse_admin:MinhaSenhaSegura123@psql-startse-server.postgres.database.azure.com:5432/startse_db`
5.  Salve e reinicie a aplicação.

### Verificação

Após configurar e reiniciar, o script `startup.sh` executará automaticamente:
```bash
python manage.py migrate --noinput
```
Isso aplicará todas as migrações pendentes no banco PostgreSQL conectado, resolvendo erros como `no such column`.
