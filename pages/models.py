from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.templatetags.static import static

class Profile(AbstractUser):
    bio = models.TextField(max_length=100, blank=True,null=True)
    phone_number = PhoneNumberField(max_length=25, region='US')
    birth_date = models.DateField(blank = True, null = True) 
    is_doctor = models.BooleanField(default=False)
    verified = models.ImageField(blank=True, null=True,upload_to='doctor')
    date_created = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatar',null=True)

    gender_choices = (('others', 'Others'),('male', 'Male'),('female' ,'Female'))
    gender = models.CharField(max_length=10, choices=gender_choices,default='others')
    default_pic_mapping = { 'others': 'default.png', 'male': 'default.png', 'female': 'default.png'}

    def get_profile_pic_url(self):
        if not self.avatar:
            return static('img/{}'.format(self.default_pic_mapping[self.gender]))
        return self.avatar.url
        
class Messages(models.Model):
    sender = models.ForeignKey(Profile,related_name='sender',on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile,related_name='receiver',on_delete=models.CASCADE)
    subject = models.CharField(default='',max_length=100)
    text = models.CharField(default='',max_length=4096)
    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='contact_parent')

    def get_children(self):
        return Messages.objects.filter(parent=self)

    def __str__(self):
        return '{} to {} :{}'.format(self.sender,self.receiver,self.text)

class Calendar(models.Model):
    doctors = models.ForeignKey(Profile,related_name='doctors',on_delete=models.CASCADE)
