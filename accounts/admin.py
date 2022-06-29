from django.contrib import admin

from .models import User, Customer, UserRole,  Administrator, Token


admin.site.register(User)
admin.site.register(Customer)
admin.site.register(UserRole)
admin.site.register(Administrator)
admin.site.register(Token)
