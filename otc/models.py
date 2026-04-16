from django.db import models
from django.contrib.auth.models import User
from core.multitenancy import TenantBaseModel

class TenantProfile(models.Model):
    """
    Configuration for the white label owner (desk owner).
    This model is GLOBAL (not tenant-filtered in the same way as trades).
    """
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otc_desk')
    tenant_slug = models.SlugField(unique=True, help_text="Unique ID for URL/Subdomain")
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='otc/logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#000000', help_text="Hex color")
    
    # Default spread for this desk
    default_spread_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    
    def __str__(self):
        return f"Mesa: {self.name} ({self.tenant_slug})"

class Quote(TenantBaseModel):
    """
    Request for Quote (RFQ) record.
    """
    STATUS_CHOICES = (
        ('P', 'Pendente'),
        ('A', 'Aceita'),
        ('E', 'Expirada'),
        ('C', 'Cancelada'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base_asset = models.CharField(max_length=10) # Ex: BTC
    quote_asset = models.CharField(max_length=10, default='BRL')
    side = models.CharField(max_length=4, choices=(('BUY', 'Compra'), ('SELL', 'Venda')))
    
    volume = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Pricing info
    price_base = models.DecimalField(max_digits=20, decimal_places=8, help_text="Market price without spread")
    spread_applied = models.DecimalField(max_digits=5, decimal_places=2)
    price_final = models.DecimalField(max_digits=20, decimal_places=8, help_text="Price shown to client")
    
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Quote {self.id} | {self.side} {self.base_asset} @ {self.price_final}"

class Trade(TenantBaseModel):
    """
    Finalized transaction.
    """
    quote = models.OneToOneField(Quote, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    final_price = models.DecimalField(max_digits=20, decimal_places=8)
    total_volume = models.DecimalField(max_digits=20, decimal_places=8)
    total_quote = models.DecimalField(max_digits=20, decimal_places=8, help_text="Total in BRL/USD")
    
    executed_at = models.DateTimeField(auto_now_add=True)
    
    # External reference for settlement
    tx_hash = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Trade {self.id} | {self.quote.base_asset} | {self.total_quote}"
