from orders.models import Tenant, Order, Customer
from orders.managers import _thread_locals


def test_tenant_isolation():
    tenant_a = Tenant.objects.create(name="A")
    tenant_b = Tenant.objects.create(name="B")

    customer = Customer.objects.create(name="Test")

    Order.objects.create(tenant=tenant_a, customer=customer)
    Order.objects.create(tenant=tenant_b, customer=customer)

    _thread_locals.tenant = tenant_a

    orders = Order.objects.all()

    assert all(o.tenant == tenant_a for o in orders)