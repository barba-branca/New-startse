#!/bash
# Script de inicialização para Azure

# 1. Migrações
python manage.py migrate --noinput

# 2. Estáticos
python manage.py collectstatic --noinput

# 3. Iniciar Gunicorn (o Azure precisa dele rodando na porta 8000 ou na porta da variável PORT)
gunicorn --bind=0.0.0.0:8000 --timeout 600 core.wsgi:application
