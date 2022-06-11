from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManagers


PhoneNumberValidator = RegexValidator(r'^[0-9]{10}$', 'Invalid Phone Number')
CreditCardValidator = RegexValidator(r'^[0-9]{15, 16}$', 'Invalid Credit Card')


class CustomUser(AbstractUser):
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=11, validators=[PhoneNumberValidator, ])
    credit_card = models.CharField(max_length=16, validators=[CreditCardValidator, ])

    objects = CustomUserManagers()

    @property
    def is_customer(self):
        return not self.is_staff

    @property
    def is_admin(self):
        return self.is_staff
