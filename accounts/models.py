from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import (MinimumLengthValidator, CommonPasswordValidator,
                                                     NumericPasswordValidator)

from .managers import UserManager, CustomerManager


PhoneNumberValidator = RegexValidator(r'^[0-9]{10}$', 'Invalid Phone Number')
CreditCardValidator = RegexValidator(r'^[0-9]{15, 16}$', 'Invalid Credit Card')


class UserRole(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super().save(*args, **kwargs)


class User(models.Model):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[UnicodeUsernameValidator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    password = models.CharField("Password", max_length=128, validators=[MinimumLengthValidator, CommonPasswordValidator,
                                                                        NumericPasswordValidator])
    email = models.EmailField("Email Address", blank=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)

    objects = UserManager()

    def __str__(self):
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField("First Name", max_length=150, blank=True)
    last_name = models.CharField("Last Name", max_length=150, blank=True)
    address = models.CharField("Address", max_length=150, blank=True)
    phone_number = models.CharField(max_length=11, validators=[PhoneNumberValidator, ])
    credit_card = models.CharField(max_length=16, validators=[CreditCardValidator, ])

    objects = CustomerManager()

    def __str__(self):
        return self.user.username


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField("First Name", max_length=150, blank=True)
    last_name = models.CharField("Last Name", max_length=150, blank=True)

    def __str__(self):
        return self.user.username
