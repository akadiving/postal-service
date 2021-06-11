from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'username', 'first_name', 
                    'last_name', 'company_name')
    list_filter = ('email', 'username', 'first_name', 
                    'is_active', 'is_staff', 'company_name')
    ordering = ('-created_at',)
    list_display = ('email', 'username', 'first_name',
                    'last_name','is_active', 'is_staff', 'company_name')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name','last_name', 'company_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Personal', {'fields': ('about',)}),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})},
    }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 
            'password1', 'password2', 'is_active', 'is_staff', 'company_name')}
         ),
    )
    


admin.site.register(User, UserAdminConfig)