from django.urls import path

from .views import (RegistrationView, LogInView, LogOutView, get_user_token)


app_name = 'accounts'


urlpatterns = [
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('user-token/', get_user_token, name='user_token'),
]
