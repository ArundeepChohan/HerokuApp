from django.urls import path
from pages.views import index, ContactWizard, show_message_form_condition
from pages.forms import PickUserType, SignUpForm

contact_forms = [PickUserType, SignUpForm]
urlpatterns = [
    path('', index, name='home'), 
    #path('signup/', signup, name="signup"),
    path('signup/', ContactWizard.as_view(contact_forms,
        condition_dict={'1': show_message_form_condition}
    ),name='signup'),
]
