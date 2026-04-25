import pytest
from orders.models import Tenant, Customer, Order
from orders.tenant_context import set_current_tenant, clear_current_tenant


@pytest.mark.django_db
def test_tenant_isolation():
    t1 = Tenant.objects.create(name="Tenant A")
    t2 = Tenant.objects.create(name="Tenant B")

    customer = Customer.objects.create(name="John")

    Order._base_manager.create(tenant=t1, customer=customer)
    Order._base_manager.create(tenant=t2, customer=customer)

    set_current_tenant(t1)

    assert Order.objects.count() == 1
    assert Order.objects.first().tenant == t1

    clear_current_tenant()


@pytest.mark.django_db
def test_objects_all_is_scoped():
    t1 = Tenant.objects.create(name="Tenant A")
    customer = Customer.objects.create(name="John")

    Order._base_manager.create(tenant=t1, customer=customer)

    assert Order.objects.all().count() == 0