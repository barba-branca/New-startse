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

def cadastro(request):
    if request.method == "GET":
        google_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
        context = {
            'google_client_id': google_id,
            'google_login_url': request.build_absolute_uri('/usuarios/google-login/')
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
            

@csrf_exempt
def google_login(request):
    if request.method == "POST":
        id_token = request.POST.get('credential')
        if not id_token:
            messages.add_message(request, constants.ERROR, 'Token do Google não recebido')
            return redirect('/usuarios/logar')

        # Verifica o token com o Google
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
        
        if response.status_code != 200:
            messages.add_message(request, constants.ERROR, 'Token do Google inválido')
            return redirect('/usuarios/logar')
        
        data = response.json()
        
        # Validar o Client ID (opcional mas recomendado)
        expected_client_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
        if data.get('aud') != expected_client_id:
             messages.add_message(request, constants.ERROR, 'Tentativa de login inválida: Client ID incorreto')
             return redirect('/usuarios/logar')

        email = data.get('email')
        first_name = data.get('given_name', '')
        last_name = data.get('family_name', '')
        
        # O Nome de usuário será o email ou parte dele
        username = email.split('@')[0]
        
        user = User.objects.filter(email=email).first()
        
        if not user:
            # Verifica se o username já existe
            if User.objects.filter(username=username).exists():
                username = f"{username}{random.randint(100, 999)}"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_unusable_password()
            user.save()
            
        auth.login(request, user)
        messages.add_message(request, constants.SUCCESS, 'Autenticado com sucesso via Google!')
        return redirect('/empresarios/cadastrar_empresa/')
    
    return redirect('/usuarios/logar')

        
def logar(request):
    if request.method == "GET":
        google_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
        context = {
            'google_client_id': google_id,
            'google_login_url': request.build_absolute_uri('/usuarios/google-login/')
        }
        return render(request, 'logar.html', context)
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)
        if  user:
            auth.login(request, user)
            return redirect('/empresarios/cadastrar_empresa')
        messages.add_message(request, constants.ERROR, 'Usuario ou senha invalida')
        return redirect('/usuarios/logar')