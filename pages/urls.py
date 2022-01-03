from django.urls import path
from pages.views import  index, buttonSelection, UserWizard, DoctorWizard

urlpatterns = [
    path('', index, name='home'), 
    path('signup/', buttonSelection, name='signup'), 
    path('user/', UserWizard.as_view() , name='user'), 
    path('doctor/',DoctorWizard.as_view(), name='doctor'),
]
