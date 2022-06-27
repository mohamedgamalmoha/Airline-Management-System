from django.contrib import admin

from .models import User, Customer, UserRole,  Administrator


admin.site.register(User)
admin.site.register(Customer)
admin.site.register(UserRole)
admin.site.register(Administrator)
