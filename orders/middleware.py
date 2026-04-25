from .models import Tenant
from .tenant_context import set_current_tenant, clear_current_tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = request.headers.get("X-Tenant")

        if tenant_id:
            tenant = Tenant.objects.filter(id=tenant_id).first()
            set_current_tenant(tenant)

        try:
            response = self.get_response(request)
        finally:
            clear_current_tenant()

        return response