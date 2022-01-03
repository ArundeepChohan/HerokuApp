
from django.shortcuts import redirect, render
from .forms import SignUpForm, UserProfileForm, verify
from django.contrib.auth import login, authenticate

from formtools.wizard.views import SessionWizardView

def buttonSelection(request):
    return render(request,'pickUserType.html')

def process_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    print(form_data)
    return form_data
    
## Issue using createUser view
""" WIZARD_FORMS = [("0" , SignUpForm),]
TEMPLATES = {"0": "createUser.html"} """
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
class DoctorWizard(SessionWizardView):
    verified = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'doctor'))
    template_name = "registration/signup.html"
    form_list=[SignUpForm,verify]
    
    def done(self, form_list, **kwargs):
        process_data(form_list)
        return redirect('home')
        
class UserWizard(SessionWizardView):
    template_name = "registration/signup.html"
    form_list=[SignUpForm]
    def done(self, form_list, **kwargs):
        process_data(form_list)
        return redirect('home')
""" 
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]
 """
def userForm(request):
    return render(request,'createUser.html')

def doctorForm(request):
    return render(request,'createUser.html')

""" def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form}) """

def index(request):
    context = {'is_post': False}
    if request.method == "POST":
        context['is_post'] = True
        form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home') 
    else:
        # Checks if user is logged out or in and passes to form
        if request.user.is_authenticated:
            form = UserProfileForm(instance=request.user)
        else:
            form = UserProfileForm()

    context['form']= form
    return render(request, "home.html", context)