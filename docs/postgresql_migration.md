# Guia de Migração para PostgreSQL

Este documento explica como migrar seu banco de dados de SQLite para PostgreSQL na plataforma **New Start-se**.

## 1. Configuração do Ambiente

Certifique-se de que o PostgreSQL está instalado e rodando (localmente ou via serviço como Neon.tech).

### No arquivo `.env`:
Atualize sua `DATABASE_URL` seguindo o exemplo abaixo:
```env
# Exemplo Local
DATABASE_URL=postgres://usuario:senha@localhost:5432/nome_do_banco

# Exemplo Neon.tech (Recomendado para Vercel)
DATABASE_URL=postgres://user:pass@ep-hostname.us-east-2.aws.neon.tech/neondb?sslmode=require
DB_SSL_REQUIRE=True
```

## 2. Processo de Migração

### Opção A: Inicialização Limpa (Recomendada)
Se você não precisa dos dados atuais do SQLite:
1. Altere a `DATABASE_URL` no `.env`.
2. Delete todos os arquivos na pasta `otc/migrations/` (exceto `__init__.py`).
3. Execute:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Opção B: Migração de Dados Existentes
Para mover dados do SQLite para o Postgres:
1. **Exportar dados do SQLite**:
   ```bash
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
   ```
2. **Alterar para Postgres** no `.env`.
3. **Criar as tabelas**:
   ```bash
   python manage.py migrate
   ```
4. **Importar dados**:
   ```bash
   python manage.py loaddata data.json
   ```

## 3. Considerações para Vercel
Ao subir para a Vercel, você **DEVE** cadastrar as variáveis `DATABASE_URL` e `DB_SSL_REQUIRE` no painel de configurações para que a conexão funcione corretamente.

---
**Guia técnico de infraestrutura.**
