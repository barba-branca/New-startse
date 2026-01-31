#!/bin/bash

# Script de inicialização para Azure App Service

# 1. Aplicar migrações
python manage.py migrate --noinput

# 2. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 3. Iniciar o Gunicorn
gunicorn --bind=0.0.0.0:8000 --timeout 600 core.wsgi:application
