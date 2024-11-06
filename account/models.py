from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from core import settings
from warehouse.models import Warehouse


class UserManager(BaseUserManager):
    def create_user(self, phone_number, last_name, name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('User must have a phone number')
        if not name:
            raise ValueError('User must have a name')
        if not last_name:
            raise ValueError('User must have a last name')



        user = self.model(
            phone_number=phone_number,
            name=name,
            last_name=last_name,

            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, last_name, name, password, **extra_fields)


PHONE_REGEX = RegexValidator(
    regex=r"^\+998([0-9][0-9]|99)\d{7}$",
    message="Please provide a valid phone number",
)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    phone_number = models.CharField(validators=[PHONE_REGEX], max_length=21, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator_user', null=True, blank=True)
    is_admin = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name', 'last_name']

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return f'{self.name} {self.last_name}'


