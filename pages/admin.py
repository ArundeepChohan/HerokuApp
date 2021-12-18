from django.contrib import admin

#Extends user with a model with additional fields
from .models import Profile

admin.site.register(Profile)