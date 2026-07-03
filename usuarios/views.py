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
        role = request.POST.get('role')
        cnpj = request.POST.get('cnpj')

        # Valida campos obrigatórios
        if not username or not senha or not confirmar_senha or not role or not cnpj:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos obrigatórios')
            return redirect('/usuarios/cadastro')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/usuarios/cadastro')

        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha precisa ter pelo menos 6 digitos')
            return redirect('/usuarios/cadastro')

        # Verifica se username já existe
        if User.objects.filter(username=username).exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username')
            return redirect('/usuarios/cadastro')

        # Valida CNPJ usando a API de utilidades
        from empresarios.utils import validar_cnpj_api
        from .models import PerfilUsuario
        import re
        
        # Limpa o CNPJ de pontuações
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        
        # Verifica se o CNPJ já está cadastrado no sistema
        if PerfilUsuario.objects.filter(cnpj=cnpj_limpo).exists():
            messages.add_message(request, constants.ERROR, 'Este CNPJ já está cadastrado em outra conta')
            return redirect('/usuarios/cadastro')

        cnpj_valido = validar_cnpj_api(cnpj_limpo)
        if not cnpj_valido.get('valido', False):
            messages.add_message(request, constants.ERROR, f"Erro no CNPJ: {cnpj_valido.get('erro', 'CNPJ inválido')}")
            return redirect('/usuarios/cadastro')

        razao_social = cnpj_valido.get('razao_social', 'Razão Social Não Informada')

        # Cria o usuário Django
        email = username if '@' in str(username) else f"{username}@newstartse.com.br"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )
        
        # Cria o PerfilUsuario correspondente
        PerfilUsuario.objects.create(
            user=user,
            role=role,
            cnpj=cnpj_limpo,
            razao_social=razao_social
        )
        
        messages.add_message(request, constants.SUCCESS, f'Cadastro de "{razao_social}" realizado com sucesso! Faça login.')
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