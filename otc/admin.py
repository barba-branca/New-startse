from django.contrib import admin
from .models import TenantProfile, Quote, Trade

class BaseTenantAdmin(admin.ModelAdmin):
    """
    Base Admin that restricts views to the user's specific tenant.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # If user is a desk owner, they should only see their own tenant data
        # We assume the user has a TenantProfile linked to them
        try:
            user_tenant = request.user.otc_desk
            return qs.filter(tenant_id=user_tenant.tenant_slug)
        except AttributeError:
            # If user has no desk, they shouldn't see anything (or only public)
            return qs.none()

    def save_model(self, request, obj, form, change):
        # Automatically set tenant_id on save if not present
        if not obj.tenant_id and not request.user.is_superuser:
            try:
                obj.tenant_id = request.user.otc_desk.tenant_slug
            except AttributeError:
                pass
        super().save_model(request, obj, form, change)

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant_slug', 'owner', 'default_spread_percentage')
    search_fields = ('name', 'tenant_slug')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Simple owners can only see their own profile
        return qs.filter(owner=request.user)

@admin.register(Quote)
class QuoteAdmin(BaseTenantAdmin):
    list_display = ('id', 'user', 'base_asset', 'side', 'price_final', 'status', 'created_at')
    list_filter = ('status', 'base_asset', 'side')
    readonly_fields = ('tenant_id', 'created_at')

@admin.register(Trade)
class TradeAdmin(BaseTenantAdmin):
    list_display = ('id', 'user', 'total_quote', 'executed_at')
    readonly_fields = ('tenant_id', 'executed_at', 'total_quote')
