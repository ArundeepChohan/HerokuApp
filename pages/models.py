from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(AbstractUser):
    
    user = models.OneToOneField(User,related_name='profile', unique=True, on_delete=models.CASCADE)
    """ bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    birth_date = models.DateField(null=True, blank=True) """
    avatar = models.ImageField(default='default.png', upload_to='users/', null=True, blank=True)
   
    REQUIRED_FIELDS = ('username',)
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()