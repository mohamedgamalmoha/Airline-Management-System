from django.db import models
from django.contrib.auth.models import UserManager


class CustomerManager(models.Manager):

    def get_customer_by_username(self, username: str):
        return self.get(user__username=username)


class CustomUserManager(UserManager):
    def get_user_by_username(self, username: str):
        return self.get(username=username)
