from django.db import models
from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    
    """ bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    birth_date = models.DateField(null=True, blank=True) """
    avatar = models.ImageField(default='default.png', upload_to='')
