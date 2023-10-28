from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification, UserLastActivity


class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "is_staff"]
    list_filter = ["is_staff"]
    fieldsets = [
        (
            None,
            {"fields": ["first_name", "last_name", "username", "email", "password"]},
        ),
        ("Permissions", {"fields": ["is_staff", "is_superuser", "is_active"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]


admin.site.register(User, UserAdmin)
admin.site.register(Notification)
admin.site.register(UserLastActivity)
