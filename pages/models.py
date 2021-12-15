from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractBaseUser, PermissionsMixin):
    is_admin = models.BooleanField(default=False )
    is_superuser = models.BooleanField(default=False)
    profile_pic = models.CharField(max_length=40, unique=True)
    phone = models.CharField(max_length=40, unique=True)
    date_created = models.DateTimeField(default=timezone.now, unique=True)
    REQUIRED_FIELDS = []