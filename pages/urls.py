from django.urls import path
from pages.views import addMed, index, calendar, medications, messagesSend, messagesInbox, documents, bookAppointment, adminControls, pickUserType, UserWizard, DoctorWizard, login, logout, reply, delete, send, activate, addAppointment

urlpatterns = [
    path('', index, name='home'),
    path('accounts/login/', login, name='login'),
    path('accounts/signup/', pickUserType, name='signup'),
    path('accounts/logout/', logout, name='logout'),
    path('user/', UserWizard.as_view() , name='user'), 
    path('doctor/',DoctorWizard.as_view(), name='doctor'),
    path('medications', medications, name='medications'),
    path('calendar', calendar, name='calendar'),
    path('messagesSend', messagesSend, name='messagesSend'),
    path('messagesInbox', messagesInbox, name='messagesInbox'),
    path('documents', documents, name='documents'),
    path('bookAppointment', bookAppointment, name='bookAppointment'),
    path('adminControls', adminControls, name='adminControls'), 
    path('send/', send, name='send'),
    path('reply/<int:message_id>/', reply, name='reply'),
    path('delete/<int:message_id>/', delete, name='delete'),
    path('activate/<str:username>/', activate, name='activate'),
    path('addMed/', addMed, name='addMed'),
    path('addAppointment/<str:username>/<str:start>/',addAppointment,name='addAppointment'),
    
]