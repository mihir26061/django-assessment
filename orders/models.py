from django.db import models
from .managers import TenantManager


class Tenant(models.Model):
    name = models.CharField(max_length=100)


class Customer(models.Model):
    name = models.CharField(max_length=100)


class Item(models.Model):
    name = models.CharField(max_length=100)


class Order(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)

    objects = TenantManager()