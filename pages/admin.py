from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pages.forms import SignUpForm

from .models import Profile

class CustomUserAdmin(UserAdmin):
    add_form = SignUpForm
    model = Profile
    list_display=['username','email','is_superuser','bio','phone_number','birth_date','is_doctor','verified','date_created','avatar']
    pass

admin.site.register(Profile, CustomUserAdmin)