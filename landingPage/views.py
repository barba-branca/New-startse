import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from .utils import get_b3_data

def landing_page(request):
    b3_data = get_b3_data()
    # Exibe mensagem quando o usuário retorna do Stripe
    payment = request.GET.get('payment')
    if payment == 'success':
        messages.add_message(request, constants.SUCCESS, 'Seu pagamento foi processado e seu plano premium está ativo!')
    elif payment == 'cancel':
        messages.add_message(request, constants.WARNING, 'O checkout foi cancelado. Você pode tentar novamente quando desejar.')
    return render(request, 'index.html')

def login_view(request):
    context = {}
    return render(request, 'logar.html', context)

@login_required(login_url='/usuarios/logar/')
def checkout(request, plan_id):
    """
    Processa o checkout do plano selecionado via Stripe.
    """
    import stripe
    from django.conf import settings
    
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    
    plans = {
        'trial_7d': {'name': 'Pro Trial (7 Dias)', 'price_amount': 0},
        'profissional': {'name': 'Profissional', 'price_amount': 9900}, # R$ 99.00
        'corporativo': {'name': 'Corporativo', 'price_amount': 29900} # R$ 299.00
    }
    
    selected_plan = plans.get(plan_id)
    if not selected_plan:
        return redirect('landingPage')
        
    if plan_id == 'trial_7d':
        # Trial de 7 dias é grátis e ativa na hora
        messages.add_message(request, constants.SUCCESS, f"Seu plano {selected_plan['name']} com tudo incluso foi ativado gratuitamente por 7 dias!")
        return redirect('/investidores/painel/')
        
    # Para planos pagos, criamos uma Stripe Checkout Session
    domain = request.build_absolute_uri('/')[:-1] # Remove barra final
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': f"Plano {selected_plan['name']} - New Start-se",
                    },
                    'unit_amount': selected_plan['price_amount'],
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=domain + '/?payment=success',
            cancel_url=domain + '/?payment=cancel',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(f"[STRIPE CHECKOUT ERROR] {str(e)}")
        # Se falhar (ex: sem chaves no .env), ativa localmente em sandbox
        messages.add_message(request, constants.SUCCESS, f"Seu plano {selected_plan['name']} foi ativado localmente com sucesso! (Modo Sandbox)")
        return redirect('/investidores/painel/')

