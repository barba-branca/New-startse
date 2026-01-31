#!/bin/bash

# Script de inicialização para Azure App Service

# Executar migrações do banco de dados
python manage.py migrate --noinput

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Iniciar o servidor Gunicorn
gunicorn core.wsgi:application --bind=0.0.0.0:8000 --workers=2 --threads=4 --timeout=120
