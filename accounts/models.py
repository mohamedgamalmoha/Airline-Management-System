import os
import binascii

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from .managers import CustomUserManager, CustomerManager


PhoneNumberValidator = RegexValidator(r'^[0-9]{10}$', 'Invalid Phone Number')
CreditCardValidator = RegexValidator(r'^[0-9]{16}$', 'Invalid Credit Card')


class NumericValidator:
    def __init__(self, password):
        self.password = password
        self.validate(password)

    def validate(self, password, user=None):
        if password.strip().isnumeric():
            raise ValidationError(
                self.get_help_text(),
                code='password_is_numeric',
            )

    def get_help_text(self):
        return f"Your password should not contain only numeric values"


class UserRole(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super().save(*args, **kwargs)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[UnicodeUsernameValidator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField("Email Address", blank=True)
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, null=True, blank=True, db_constraint=False)

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
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


class Token(models.Model):
    user = models.OneToOneField(
        User, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="User"
    )
    name = models.CharField("Key", max_length=40, blank=True)
    created = models.DateTimeField("Created", auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.name

    @property
    def username(self):
        return self.user.username

# booking twice               | T |
# auto generation token       | T |
# credit card while booking   | T |
# max number of tickets       | T |
# upload on server            | F |


@receiver(post_save, sender=User)
def create_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(
            user=instance
        )
