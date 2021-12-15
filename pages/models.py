from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractBaseUser, PermissionsMixin):
    #is_staff = models.BooleanField(default=False)
    #is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)
    #profile_pic = models.

    REQUIRED_FIELDS = []


    def __str__(self):
        return self.user