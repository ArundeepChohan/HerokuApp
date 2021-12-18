from django.contrib import admin

#Extends user with a model Profile with additional fields
from .models import Profile

admin.site.register(Profile)