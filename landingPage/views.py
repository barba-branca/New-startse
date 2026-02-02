import os
from django.shortcuts import render

def landing_page(request):
    return render(request, 'index.html')  # Refere-se ao template diretamente dentro de 'templates'

def login_view(request):
    google_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
    context = {
        'google_client_id': google_id,
        'google_login_url': request.build_absolute_uri('/usuarios/google-login/')
    }
    return render(request, 'logar.html', context)
