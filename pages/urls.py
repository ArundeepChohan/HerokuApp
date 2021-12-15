from django.urls import path
from django.views.generic.base import TemplateView # new
from django.conf import settings  # new
from django.conf.urls.static import static  # new
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
if settings.DEBUG:
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)