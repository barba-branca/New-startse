from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .services import RFQService
import json

@login_required
@csrf_exempt
def request_quote(request):
    """
    API view to request an OTC quote.
    """
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        base_asset = data.get('asset', 'BTC').upper()
        volume = float(data.get('volume', 0))
        side = data.get('side', 'BUY').upper()
        
        if volume <= 0:
            return JsonResponse({'error': 'Volume invalid'}, status=status)
            
        quote = RFQService.create_quote(request.user, base_asset, volume, side)
        
        return JsonResponse({
            'quote_id': quote.id,
            'price': float(quote.price_final),
            'total_brl': float(quote.price_final * quote.volume),
            'expires_at': quote.expires_at.isoformat(),
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
def execute_trade(request):
    """
    API view to execute a previously generated quote.
    """
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        quote_id = data.get('quote_id')
        
        trade = RFQService.execute_trade(quote_id, request.user)
        
        return JsonResponse({
            'trade_id': trade.id,
            'status': 'executed',
            'amount': float(trade.total_quote),
            'timestamp': trade.executed_at.isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ============================================================================
# STRIPE CONNECT INTEGRATION
# ============================================================================
import stripe
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .stripe_models import StripeAccount, StripePayment, PlatformFee, StripeCustomer
from .models import TenantProfile, Trade

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

@login_required
def stripe_onboarding(request):
    """
    Initializes custom connect onboarding for the tenant (desk owner)
    and returns a redirect URL to complete KYC/AML on Stripe.
    """
    profile = TenantProfile.objects.filter(owner=request.user).first()
    if not profile:
        return JsonResponse({'error': 'Only Tenant/Desk owners can onboard with Stripe.'}, status=403)

    stripe_account, created = StripeAccount.objects.get_or_create(tenant=profile)

    try:
        # Create Stripe Connected Account if not yet created
        if not stripe_account.account_id:
            account = stripe.Account.create(
                type="custom",
                country="BR",
                email=request.user.email,
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                business_type="individual"
            )
            stripe_account.account_id = account.id
            stripe_account.save()

        # Build absolute redirect URLs
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return_url = f"{scheme}://{host}/otc/stripe/onboarding/callback/?status=success&tenant_id={profile.id}"
        refresh_url = f"{scheme}://{host}/otc/stripe/onboarding/callback/?status=refresh&tenant_id={profile.id}"

        # Create Stripe Account Link for onboarding flow
        account_link = stripe.AccountLink.create(
            account=stripe_account.account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )
        
        return redirect(account_link.url)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def stripe_onboarding_callback(request):
    """
    Handle Stripe onboarding redirects. Sincroniza e valida o status da conta.
    """
    status = request.GET.get('status')
    tenant_id = request.GET.get('tenant_id')
    
    profile = get_object_or_404(TenantProfile, id=tenant_id)
    stripe_account = get_object_or_404(StripeAccount, tenant=profile)
    
    try:
        # Retrieve latest details from Stripe
        acct = stripe.Account.retrieve(stripe_account.account_id)
        if acct.details_submitted:
            stripe_account.onboarding_complete = True
            stripe_account.save()
            messages.success(request, "Cadastro do Stripe Connect concluído com sucesso!")
        else:
            messages.warning(request, "O cadastro não foi finalizado. Por favor, conclua o onboarding para poder transacionar.")
    except Exception as e:
        messages.error(request, f"Erro ao validar cadastro no Stripe: {str(e)}")
        
    return redirect('/')

@login_required
@csrf_exempt
def create_payment_intent(request):
    """
    Creates a Stripe PaymentIntent with Destination Charges.
    """
    if request.method != "POST":
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        trade_id = data.get('trade_id')
        trade = get_object_or_404(Trade, id=trade_id)
        
        # Verify Tenant Connected Account
        tenant_profile = TenantProfile.objects.filter(tenant_slug=trade.tenant_id).first()
        if not tenant_profile:
            return JsonResponse({'error': 'Tenant desk not found.'}, status=404)
            
        stripe_account = StripeAccount.objects.filter(tenant=tenant_profile, onboarding_complete=True).first()
        if not stripe_account:
            return JsonResponse({'error': 'Stripe Connect is not configured or completed for this desk.'}, status=400)
            
        # Get or create Stripe Customer for investor/buyer
        stripe_customer, _ = StripeCustomer.objects.get_or_create(user=trade.user)
        if not stripe_customer.customer_id:
            customer = stripe.Customer.create(
                email=trade.user.email,
                name=trade.user.get_full_name() or trade.user.username
            )
            stripe_customer.customer_id = customer.id
            stripe_customer.save()
            
        # Platform fee calculation
        fee_config = PlatformFee.objects.filter(active=True).first()
        fee_percentage = fee_config.fee_percentage if fee_config else Decimal('2.00')
        fee_flat = fee_config.fee_flat if fee_config else Decimal('0.00')
        
        total_amount = trade.total_quote
        platform_fee_amount = (total_amount * (fee_percentage / Decimal('100.00'))) + fee_flat
        
        amount_cents = int(total_amount * 100)
        fee_cents = int(platform_fee_amount * 100)
        
        # Destination charge to Tenant connected account
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='brl',
            customer=stripe_customer.customer_id,
            application_fee_amount=fee_cents,
            transfer_data={
                'destination': stripe_account.account_id,
            },
            metadata={
                'trade_id': trade.id,
                'tenant_id': tenant_profile.id,
            }
        )
        
        # Register StripePayment record
        stripe_payment = StripePayment.objects.create(
            payment_intent_id=intent.id,
            amount=total_amount,
            platform_fee=platform_fee_amount,
            tenant_amount=total_amount - platform_fee_amount,
            stripe_account=stripe_account,
            status='pending'
        )
        
        trade.stripe_payment = stripe_payment
        trade.save()
        
        return JsonResponse({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': float(total_amount)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    """
    Handle webhook notifications from Stripe.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    try:
        if webhook_secret and sig_header:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # Dev Mode / Manual webhook validation
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
        
    event_type = event.get('type')
    
    if event_type == 'payment_intent.succeeded':
        intent = event.data.object
        payment_intent_id = intent.id
        try:
            payment = StripePayment.objects.get(payment_intent_id=payment_intent_id)
            payment.status = 'succeeded'
            payment.save()
            
            # Settle associated Trade
            trade = Trade.objects.filter(stripe_payment=payment).first()
            if trade:
                charge_id = intent.charges.data[0].id if intent.charges.data else f"stripe_{intent.id}"
                trade.tx_hash = charge_id
                trade.save()
        except StripePayment.DoesNotExist:
            pass
            
    elif event_type == 'payment_intent.payment_failed':
        intent = event.data.object
        try:
            payment = StripePayment.objects.get(payment_intent_id=intent.id)
            payment.status = 'failed'
            payment.save()
        except StripePayment.DoesNotExist:
            pass
            
    elif event_type == 'account.updated':
        account = event.data.object
        try:
            stripe_account = StripeAccount.objects.get(account_id=account.id)
            if account.details_submitted and account.charges_enabled:
                stripe_account.onboarding_complete = True
            else:
                stripe_account.onboarding_complete = False
            stripe_account.save()
        except StripeAccount.DoesNotExist:
            pass
            
    return JsonResponse({'status': 'processed'})

@login_required
@csrf_exempt
def stripe_saas_subscribe(request):
    """
    Initializes setup intent for future SaaS monthly subscription billing for Tenants.
    """
    try:
        stripe_customer, _ = StripeCustomer.objects.get_or_create(user=request.user)
        if not stripe_customer.customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.username
            )
            stripe_customer.customer_id = customer.id
            stripe_customer.save()
            
        # Create SetupIntent to collect credit card info for recurring billing (SaaS)
        setup_intent = stripe.SetupIntent.create(
            customer=stripe_customer.customer_id,
            payment_method_types=['card'],
            usage='off_session'
        )
        
        return JsonResponse({
            'client_secret': setup_intent.client_secret,
            'setup_intent_id': setup_intent.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

