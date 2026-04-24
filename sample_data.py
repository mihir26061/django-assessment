from orders.models import *

t = Tenant.objects.create(name="T1")
c = Customer.objects.create(name="John")

for i in range(200):
    o = Order.objects.create(tenant=t, customer=c)