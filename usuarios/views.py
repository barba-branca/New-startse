import os
import requests
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# def get_google_id():
#     """Retorna o ID do Google com fallback para evitar o erro 'invalid_client' - COMENTADO: conexões Gmail desativadas"""
#     gid = getattr(settings, 'GOOGLE_CLIENT_ID', None) or os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
#     if not gid or str(gid).strip() == "None" or str(gid).strip() == "":
#         return '387105332982-m1sqi0sla8sf1rr6mnae0n0rpodm9vjc.apps.googleusercontent.com'
#     return str(gid).strip()

def cadastro(request):
    if request.method == "GET":
        # google_id = get_google_id()
        # login_uri = request.build_absolute_uri('/usuarios/google-login/')
        # if 'azurewebsites.net' in login_uri:
        #     login_uri = login_uri.replace('http://', 'https://')
        context = {
            # 'google_client_id': google_id,
            # 'google_login_url': login_uri
        }
        return render(request, 'cadastro.html', context)
    
    elif request.method == "POST": 
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')


        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/usuarios/cadastro')

        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha precisa ter pelo menos 6 digitos')
            return redirect('/usuarios/cadastro')

        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuario com esse username')
            return redirect('/usuarios/cadastro')
       
        user = User.objects.create_user(
            username=username,
            password=senha
        )
            
        return redirect('/usuarios/logar')
            

# COMENTADO: conexões Gmail desativadas
# @csrf_exempt
# def google_login(request):
#     if request.method == "POST":
#         id_token = request.POST.get('credential')
#         if not id_token:
#             messages.add_message(request, constants.ERROR, 'Token do Google não recebido')
#             return redirect('/usuarios/logar')
#         response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
#         if response.status_code != 200:
#             messages.add_message(request, constants.ERROR, 'Token do Google inválido')
#             return redirect('/usuarios/logar')
#         data = response.json()
#         expected_client_id = get_google_id()
#         if data.get('aud') != expected_client_id:
#              messages.add_message(request, constants.ERROR, 'Tentativa de login inválida: Client ID incorreto')
#              return redirect('/usuarios/logar')
#         email = data.get('email')
#         first_name = data.get('given_name', '')
#         last_name = data.get('family_name', '')
#         username = email.split('@')[0]
#         user = User.objects.filter(email=email).first()
#         if not user:
#             if User.objects.filter(username=username).exists():
#                 username = f"{username}{random.randint(100, 999)}"
#             user = User.objects.create_user(
#                 username=username,
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name
#             )
#             user.set_unusable_password()
#             user.save()
#         auth.login(request, user)
#         messages.add_message(request, constants.SUCCESS, 'Autenticado com sucesso via Google!')
#         return redirect('/empresarios/cadastrar_empresa/')
#     return redirect('/usuarios/logar')

        
def logar(request):
    if request.method == "GET":
        # google_id = get_google_id()
        # login_uri = request.build_absolute_uri('/usuarios/google-login/')
        # if 'azurewebsites.net' in login_uri:
        #     login_uri = login_uri.replace('http://', 'https://')
        context = {
            # 'google_client_id': google_id,
            # 'google_login_url': login_uri
        }
        return render(request, 'logar.html', context)
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)
        if  user:
            auth.login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url or '/empresarios/cadastrar_empresa')
        messages.add_message(request, constants.ERROR, 'Usuario ou senha invalida')
        return redirect('/usuarios/logar')