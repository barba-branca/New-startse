import os
import sys
import django

# Setup django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User
from otc.models import TenantProfile, Quote, Trade
from otc.stripe_models import StripeAccount, StripePayment, PlatformFee, StripeCustomer
import stripe

def run_tests():
    print("🧪 Starting Stripe Integration Validation Tests...")
    
    # 1. Verify Stripe API Key configuration
    from django.conf import settings
    stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if stripe_key:
        print(f"✅ Stripe Secret Key is configured: {stripe_key[:10]}...")
    else:
        print("❌ Stripe Secret Key is NOT configured in settings.")
        sys.exit(1)

    # 2. Test PlatformFee Model creation
    print("\nTesting PlatformFee model...")
    # Delete any existing test platform fees
    PlatformFee.objects.filter(fee_percentage=2.5, fee_flat=5.0).delete()
    fee = PlatformFee.objects.create(
        fee_percentage=2.50,
        fee_flat=5.00,
        active=True
    )
    print(f"✅ PlatformFee created successfully: {fee}")
    
    # Verify retrieval
    active_fee = PlatformFee.objects.filter(active=True).first()
    assert active_fee is not None
    assert active_fee.fee_percentage == 2.50
    print("✅ PlatformFee query works.")

    # 3. Test StripeCustomer Model
    print("\nTesting StripeCustomer model...")
    # Create or get test user
    user, created = User.objects.get_or_create(username="stripe_test_user", email="test@stripe.com")
    StripeCustomer.objects.filter(user=user).delete()
    customer = StripeCustomer.objects.create(
        user=user,
        customer_id="cus_test12345"
    )
    print(f"✅ StripeCustomer created: {customer}")
    
    # 4. Test StripeAccount Model
    print("\nTesting StripeAccount model...")
    # Create or get test tenant profile
    tenant_profile, created = TenantProfile.objects.get_or_create(
        owner=user,
        tenant_slug="test-desk-stripe",
        name="Test Desk Stripe",
        default_spread_percentage=1.50
    )
    StripeAccount.objects.filter(tenant=tenant_profile).delete()
    stripe_account = StripeAccount.objects.create(
        tenant=tenant_profile,
        account_id="acct_test12345",
        onboarding_complete=False
    )
    print(f"✅ StripeAccount created: {stripe_account}")
    
    # 5. Test StripePayment & Trade linking
    print("\nTesting StripePayment & Trade relation...")
    payment = StripePayment.objects.create(
        payment_intent_id="pi_test12345",
        amount=1000.00,
        platform_fee=30.00,
        tenant_amount=970.00,
        stripe_account=stripe_account,
        status="pending"
    )
    print(f"✅ StripePayment created: {payment}")

    # Create dummy Quote for Trade
    from django.utils import timezone
    quote = Quote.objects.create(
        user=user,
        base_asset="BTC",
        volume=0.1,
        price_base=10000.00,
        spread_applied=1.50,
        price_final=10150.00,
        status="A",
        expires_at=timezone.now() + timezone.timedelta(minutes=5),
        tenant_id="test-desk-stripe"
    )
    
    trade = Trade.objects.create(
        quote=quote,
        user=user,
        final_price=10150.00,
        total_volume=0.1,
        total_quote=1015.00,
        stripe_payment=payment,
        tenant_id="test-desk-stripe"
    )
    print(f"✅ Trade created with StripePayment relation: {trade}")
    assert trade.stripe_payment == payment
    print("✅ Relation check passed.")
    
    # Cleanup tests records
    trade.delete()
    quote.delete()
    payment.delete()
    stripe_account.delete()
    tenant_profile.delete()
    customer.delete()
    user.delete()
    fee.delete()
    
    print("\n🎉 All Stripe database model integration tests PASSED successfully!")

if __name__ == "__main__":
    run_tests()
