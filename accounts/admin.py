from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, ShippingAddress, OTPVerification

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'is_verified', 'is_staff', 'date_joined']
    list_filter = ['is_verified', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ['email']
    ordering = ['email']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(ShippingAddress)
admin.site.register(OTPVerification)