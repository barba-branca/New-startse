import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from .utils import get_b3_data, create_checkout_preference

def landing_page(request):
    b3_data = get_b3_data()
    # Exibe mensagem quando o usuário retorna do Mercado Pago
    status = request.GET.get('status')
    if status == 'failure':
        messages.add_message(request, constants.ERROR, 'O pagamento não foi aprovado. Tente novamente ou entre em contato.')
    elif status == 'pending':
        messages.add_message(request, constants.WARNING, 'Seu pagamento está em análise. Você receberá uma confirmação em breve.')
    return render(request, 'index.html', {'b3_data': b3_data})

def login_view(request):
    # COMENTADO: conexões Gmail desativadas
    # google_id = os.getenv('GMAIL_API_KEY') or os.getenv('GOOGLE_CLIENT_ID')
    # if not google_id or str(google_id).strip() == "None" or str(google_id).strip() == "":
    #     google_id = '387105332982-m1sqi0sla8sf1rr6mnae0n0rpodm9vjc.apps.googleusercontent.com'
    # login_uri = request.build_absolute_uri('/usuarios/google-login/')
    # if 'azurewebsites.net' in login_uri:
    #     login_uri = login_uri.replace('http://', 'https://')
    context = {
        # 'google_client_id': google_id,
        # 'google_login_url': login_uri
    }
    return render(request, 'logar.html', context)

@login_required(login_url='/usuarios/logar/')
def checkout(request, plan_id):
    """
    Processa o checkout do plano selecionado.
    """
    plans = {
        'profissional': {'name': 'Profissional', 'price': 97.00},
        'corporativo': {'name': 'Corporativo', 'price': 297.00}
    }
    
    selected_plan = plans.get(plan_id)
    
    if not selected_plan:
        return redirect('landingPage')
        
    checkout_url, erro = create_checkout_preference(
        request,
        request.user,
        selected_plan['name'],
        selected_plan['price']
    )

    if checkout_url:
        return redirect(checkout_url)

    messages.add_message(request, constants.ERROR, erro or "Erro ao processar pagamento.")
    return redirect('landingPage')

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import mercadopago

@csrf_exempt
def webhook_mercadopago(request):
    """
    Recebe notificações (IPN) do Mercado Pago.
    """
    if request.method == 'POST':
        topic = request.GET.get('topic') or request.GET.get('type')
        id = request.GET.get('id') or request.GET.get('data.id')

        if not topic or not id:
            # Tenta pegar do corpo se não vier na URL
            try:
                body = json.loads(request.body)
                topic = body.get('type')
                id = body.get('data', {}).get('id')
            except:
                pass

        if topic == 'payment':
            sdk = mercadopago.SDK(os.getenv('MERCADO_PAGO_ACCESS_TOKEN'))
            payment_info = sdk.payment().get(id)
            
            if payment_info['status'] == 200:
                payment = payment_info['response']
                status = payment.get('status')
                external_reference = payment.get('external_reference') # Pode usar para identificar o user/pedido
                
                # LÓGICA PARA LIBERAR O PLANO
                if status == 'approved':
                    # TODO: Atualizar status do usuário no banco de dados
                    # Ex: user = User.objects.get(id=external_reference)
                    # user.plano = 'pago'
                    # user.save()
                    print(f"Pagamento APROVADO: {id}")
                else:
                    print(f"Pagamento {status}: {id}")
            
            return HttpResponse(status=200)
            
    return HttpResponse(status=200)
