from django.core.validators import RegexValidator
from django.db import models

from core import settings

PHONE_REGEX = RegexValidator(
    regex=r"^\+998([0-9][0-9]|99)\d{7}$",
    message="Please provide a valid phone number",
)
class Warehouse(models.Model):
    name = models.CharField(max_length=260, unique=True, )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_warehouse')
    address = models.CharField(max_length=250)
    phone_number = models.CharField(validators=[PHONE_REGEX], max_length=21, default="+998977777777")
    description = models.TextField(null=True, blank=True)


    def __str__(self):
            return self.name


class Category(models.Model):
    name = models.CharField(max_length=260, unique=True, )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)



    def __str__(self):
            return self.name
