from django.urls import path
from pages.views import index, buttonSelection, UserWizard, DoctorWizard, login, reply, delete, send
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', index, name='home'),
    path('accounts/login/', login, name='login'),
    path('signup/', buttonSelection, name='signup'), 
    path('user/', UserWizard.as_view() , name='user'), 
    path('doctor/',DoctorWizard.as_view(), name='doctor'),
    path('send', send, name='send'),
    path('reply/<int:messageID>/', reply, name='reply'),
    path('delete/<int:messageID>/', delete, name='delete'),
]
