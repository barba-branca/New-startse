import os
from django.shortcuts import render
from .utils import get_b3_data

def landing_page(request):
    b3_data = get_b3_data()
    return render(request, 'index.html', {'b3_data': b3_data})

def login_view(request):
    google_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
    # Fallback definitivo para evitar o erro 'invalid_client' na Azure
    if not google_id or str(google_id).strip() == "None" or str(google_id).strip() == "":
        google_id = '387105332982-m1sqi0sla8sf1rr6mnae0n0rpodm9vjc.apps.googleusercontent.com'
    
    login_uri = request.build_absolute_uri('/usuarios/google-login/')
    
    if 'azurewebsites.net' in login_uri:
        login_uri = login_uri.replace('http://', 'https://')

    context = {
        'google_client_id': google_id,
        'google_login_url': login_uri
    }
    return render(request, 'logar.html', context)
