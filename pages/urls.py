from django.conf import settings
from django.urls import path
from django.views.generic.base import TemplateView # new

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)