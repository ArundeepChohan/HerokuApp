from django.urls import path
from pages.views import index

urlpatterns = [
    path('', index, name='home'), 
]
