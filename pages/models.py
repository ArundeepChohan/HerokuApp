from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class Profile(AbstractUser):
    bio = models.TextField(max_length=100, blank=True)
    phone_number = PhoneNumberField(max_length=25, region="US")
    birth_date = models.DateField(blank = True, null = True) 
    is_doctor = models.BooleanField(default=False)
    verified = models.ImageField(upload_to='media/doctor')
    date_created = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(default='default.png', upload_to='')
    #status = models.BooleanField(default=False)
