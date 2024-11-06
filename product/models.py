from django.db import models
from django.utils import timezone
from warehouse.models import Warehouse, Category
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    name = models.CharField(max_length=250)
    cost = models.IntegerField()
    amount = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    add_time = models.DateTimeField(default=timezone.now)
    Type = [
        ('yangi', _('Yangi')),
        ('sotildi', _('Sotildi')),
    ]
    status = models.CharField(max_length=500, choices=Type)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
            return self.name



class SoldProduct(models.Model):
    name = models.CharField(max_length=250)
    cost = models.IntegerField()
    amount = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    add_time = models.DateTimeField(default=timezone.now)
    Type = [
        ('yangi', _('Yangi')),
        ('sotildi', _('Sotildi')),
    ]
    status = models.CharField(max_length=500, choices=Type)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

