from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.templatetags.static import static

class Profile(AbstractUser):
    bio = models.TextField(max_length=100, blank=True,null=True)
    phone_number = PhoneNumberField(max_length=25, region='US')
    birth_date = models.DateField(blank = True, null = True) 
    is_doctor = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatar',null=True)
    verified = models.ImageField(blank=True, null=True,upload_to='doctor')

    gender_choices = (('others', 'Others'),('male', 'Male'),('female' ,'Female'))
    gender = models.CharField(max_length=10, choices=gender_choices,default='others')
    default_pic_mapping = { 'others': 'default.png', 'male': 'default.png', 'female': 'default.png'}

    def get_profile_pic_url(self):
        if not self.avatar:
            return static('img/{}'.format(self.default_pic_mapping[self.gender]))
        return self.avatar.url

class Messages(models.Model):
    sender = models.ForeignKey(Profile,related_name='sender',on_delete=models.CASCADE)
    senderDeleted = models.BooleanField(default=False)
    receiver = models.ForeignKey(Profile,related_name='receiver',on_delete=models.CASCADE)
    receiverDeleted = models.BooleanField(default=False)
    subject = models.CharField(default='',max_length=100)
    text = models.CharField(default='',max_length=4096)
    time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='contact_parent')

    def get_children(self):
        return Messages.objects.filter(parent=self)

    def __str__(self):
        return '{} to {} :{}'.format(self.sender,self.receiver,self.text)

class Medications(models.Model):
    user = models.ForeignKey(Profile,related_name='user',on_delete=models.CASCADE)
    name = models.CharField(default='',max_length=100)
    dosage = models.IntegerField()
    times = models.IntegerField()
    time_choices = (('other', 'Other'),('Breakfast' ,'Breakfast'))
    type_choices = (('other', 'Other'),('Post meal', 'Post meal'))
    choice = models.CharField(max_length=10, choices=time_choices,default='others')
    type = models.CharField(max_length=10, choices=type_choices,default='others')

class Calendar(models.Model):
    doctors = models.ForeignKey(Profile,related_name='doctors',on_delete=models.CASCADE)
