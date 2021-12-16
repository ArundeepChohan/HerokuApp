from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractBaseUser, PermissionsMixin):
    #Do you need all permissions
    is_superuser = models.BooleanField(default=False)
    #Can you log into /admin
    is_staff = models.BooleanField(default=False)
    #Are you a patient or doctor
    is_doctor = models.BooleanField(default=False)
    #Value for AWS S3 bucket 
    profile_pic = models.ImageField(default="profile1.png", null=True, blank=True)
    phone = models.CharField(max_length=40, unique=True)
    date_created = models.DateTimeField(default=timezone.now, unique=True)
    REQUIRED_FIELDS = []