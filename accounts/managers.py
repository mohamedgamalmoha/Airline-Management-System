from django.contrib.auth.models import UserManager


class CustomUserManagers(UserManager):

    def get_customer_by_username(self, username):
        return self.get(username=username, is_staff=False)

    def get_user_by_username(self, username):
        return self.get(username=username, is_staff=True)
