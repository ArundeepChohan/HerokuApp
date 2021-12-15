from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
class UserAdminCustom(BaseUserAdmin):
   list_display = ('email', 'phone', 'profile-pic','date-created', 'is_staff', 'is_superuser')
   list_filter = ('is_staff', 'is_superuser')
   search_fields = ('username', )

admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)