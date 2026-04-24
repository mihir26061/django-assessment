from .managers import _thread_locals
from .models import Tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Simulated tenant (header-based)
        tenant_id = request.headers.get("X-Tenant")

        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                _thread_locals.tenant = tenant
            except Tenant.DoesNotExist:
                _thread_locals.tenant = None

        response = self.get_response(request)

        _thread_locals.tenant = None
        return response