# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalação das dependências Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Instalação de bibliotecas de execução necessárias (como libpq para PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copia as dependências do builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copia o código da aplicação
COPY . .

# Variáveis de ambiente padrão
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Coleta arquivos estáticos durante o build do container
# Nota: DATABASE_URL temporário para não quebrar o collectstatic se o app validar conexão
RUN python manage.py collectstatic --noinput

# Comando de inicialização usando gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "core.wsgi:application"]
