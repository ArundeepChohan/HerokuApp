from django.urls import path
from pages.views import  index, calendar, messagesSend, messagesInbox, documents, bookAppointment, adminControls, pickUserType, UserWizard, DoctorWizard, login, reply, delete, send, activate

urlpatterns = [
    path('', index, name='home'),
    path('accounts/login/', login, name='login'),
    path('accounts/signup/', pickUserType, name='signup'),
    path('user/', UserWizard.as_view() , name='user'), 
    path('doctor/',DoctorWizard.as_view(), name='doctor'),
    path('calendar', calendar, name='calendar'),
    path('messagesSend', messagesSend, name='messagesSend'),
    path('messagesInbox', messagesInbox, name='messagesInbox'),
    path('documents', documents, name='documents'),
    path('bookAppointment', bookAppointment, name='bookAppointment'),
    path('adminControls', adminControls, name='adminControls'), 
    path('send/', send, name='send'),
    path('reply/<int:messageID>/', reply, name='reply'),
    path('delete/<int:messageID>/', delete, name='delete'),
    path('activate/<str:username>/', activate, name='activate'),
]