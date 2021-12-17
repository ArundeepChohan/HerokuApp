from django.conf import settings
from django.urls import path
from django.views.generic.base import TemplateView # new

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
