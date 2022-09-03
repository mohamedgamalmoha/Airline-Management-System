from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Customer, UserRole,  Administrator, Token


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff')
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    sortable_by = ('date_of_creation',)
    ordering = ('-date_joined',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'role', 'password1', 'password2')}
         ),
    )

    # def get_readonly_fields(self, request, obj=None):
    #     return super(UserAdmin, self).get_readonly_fields(request, obj) if obj else ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer)
admin.site.register(UserRole)
admin.site.register(Administrator)
admin.site.register(Token)
