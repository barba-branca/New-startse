import os
from django.shortcuts import render
from .utils import get_b3_data

def landing_page(request):
    b3_data = get_b3_data()
    return render(request, 'index.html', {'b3_data': b3_data})

def login_view(request):
    google_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
    login_uri = request.build_absolute_uri('/usuarios/google-login/')
    
    if 'azurewebsites.net' in login_uri:
        login_uri = login_uri.replace('http://', 'https://')

    context = {
        'google_client_id': google_id,
        'google_login_url': login_uri
    }
    return render(request, 'logar.html', context)
