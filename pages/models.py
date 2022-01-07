from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class Profile(AbstractUser):
    bio = models.TextField(max_length=100, blank=True)
    phone_number = PhoneNumberField(max_length=25, region="US")
    birth_date = models.DateField(blank = True, null = True) 
    is_doctor = models.BooleanField(default=False)
    verified = models.ImageField(default='',upload_to='doctor')
    date_created = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(default='default.png', upload_to='')

class Messages(models.Model):
    sender = models.ForeignKey(Profile,related_name='sender',on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile,related_name='receiver',on_delete=models.CASCADE)
    subject = models.CharField(default='',max_length=100)
    text = models.CharField(default='',max_length=4096)
    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return '{} to {} :{}'.format(self.sender,self.receiver,self.text)