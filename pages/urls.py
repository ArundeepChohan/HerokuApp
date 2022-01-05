from django.urls import path
from pages.views import index, buttonSelection, UserWizard, DoctorWizard
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', index, name='home'),
    # path('accounts/login/',auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', buttonSelection, name='signup'), 
    path('user/', UserWizard.as_view() , name='user'), 
    path('doctor/',DoctorWizard.as_view(), name='doctor'),
]
