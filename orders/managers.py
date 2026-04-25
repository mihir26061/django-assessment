from django.db import models
from .tenant_context import get_current_tenant


class TenantManager(models.Manager):
    def get_queryset(self):
        tenant = get_current_tenant()

        qs = super().get_queryset()

        if tenant is None:
            return qs.none()

        return qs.filter(tenant=tenant)