from django.urls import path
from . import views

app_name = 'otc'

urlpatterns = [
    path('rfq/request/', views.request_quote, name='request_quote'),
    path('rfq/execute/', views.execute_trade, name='execute_trade'),
    
    # Stripe Connect Endpoints
    path('stripe/onboarding/', views.stripe_onboarding, name='stripe_onboarding'),
    path('stripe/onboarding/callback/', views.stripe_onboarding_callback, name='stripe_onboarding_callback'),
    path('stripe/payment/intent/', views.create_payment_intent, name='create_payment_intent'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('stripe/saas/subscribe/', views.stripe_saas_subscribe, name='stripe_saas_subscribe'),
]

