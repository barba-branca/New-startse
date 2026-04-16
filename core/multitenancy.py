import threading
from django.db import models

# Thread-local storage for the current tenant ID
_thread_locals = threading.local()

def set_current_tenant_id(tenant_id):
    _thread_locals.tenant_id = tenant_id

def get_current_tenant_id():
    return getattr(_thread_locals, 'tenant_id', None)

class TenantMiddleware:
    """
    Middleware to identify the current tenant from the request.
    Can use subdomain or a custom header.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Try to get tenant from Header (useful for API)
        tenant_id = request.headers.get('X-Tenant-ID')
        
        # 2. Fallback to subdomain (e.g. mesa-a.plataforma.com)
        if not tenant_id:
            host = request.get_host().split(':')[0]
            parts = host.split('.')
            if len(parts) > 2:
                tenant_id = parts[0]
        
        # 3. If user is authenticated, we could also link them to a tenant
        # but for White Label, the URL/Header is usually the source of truth
        
        set_current_tenant_id(tenant_id)
        
        response = self.get_response(request)
        
        # Clean up
        set_current_tenant_id(None)
        
        return response

class TenantManager(models.Manager):
    """
    Manager that automatically filters queries by the current tenant.
    """
    def get_queryset(self):
        tenant_id = get_current_tenant_id()
        queryset = super().get_queryset()
        if tenant_id:
            return queryset.filter(tenant_id=tenant_id)
        return queryset

class TenantBaseModel(models.Model):
    """
    Base class for all multi-tenant models.
    """
    tenant_id = models.CharField(max_length=50, db_index=True)
    
    objects = TenantManager()
    original_objects = models.Manager() # Useful for admin/system tasks

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            self.tenant_id = get_current_tenant_id()
        super().save(*args, **kwargs)
