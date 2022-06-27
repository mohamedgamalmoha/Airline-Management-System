from django.db import models


class CustomerManager(models.Manager):

    def get_customer_by_username(self, username: str):
        return self.get(user__username=username)


class UserManager(models.Manager):
    def get_user_by_username(self, username: str):
        return self.get(username=username)
