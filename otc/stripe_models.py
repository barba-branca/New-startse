from django.db import models
from django.contrib.auth.models import User

class StripeAccount(models.Model):
    """
    Stripe Connected Account (Custom Connect) for a Tenant (Desk Owner).
    """
    tenant = models.OneToOneField('otc.TenantProfile', on_delete=models.CASCADE, related_name='stripe_account')
    account_id = models.CharField(max_length=100, unique=True)
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe Account: {self.account_id} for {self.tenant.name}"

class StripePayment(models.Model):
    """
    Detailed ledger of a Stripe transaction (split payment).
    """
    payment_intent_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='BRL')
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tenant_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, default='pending')
    stripe_account = models.ForeignKey(StripeAccount, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_intent_id} | Amount: {self.amount} {self.currency} | Status: {self.status}"

class PlatformFee(models.Model):
    """
    Global platform fee configuration.
    """
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage fee, e.g., 2.50 for 2.5%")
    fee_flat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Flat fee per transaction in currency units (e.g. 5.00)")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Platform Fee: {self.fee_percentage}% + R$ {self.fee_flat} (Active: {self.active})"

class StripeCustomer(models.Model):
    """
    Stripe Customer ID mapping for a User (Investor/Client).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_customer')
    customer_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stripe Customer: {self.customer_id} for {self.user.username}"
