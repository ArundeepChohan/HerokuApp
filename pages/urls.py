from django.conf import settings
from django.urls import path

from pages.views import index

urlpatterns = [
    path('', index, name='home'), 
]
