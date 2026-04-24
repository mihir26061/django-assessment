from django.db import models
from threading import local

_thread_locals = local()


def get_current_tenant():
    return getattr(_thread_locals, "tenant", None)


class TenantManager(models.Manager):
    def get_queryset(self):
        tenant = get_current_tenant()
        qs = super().get_queryset()
        if tenant:
            return qs.filter(tenant=tenant)
        return qs.none()