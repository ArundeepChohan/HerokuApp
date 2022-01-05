
from django.shortcuts import redirect, render
from .forms import SignUpForm, UserProfileForm, verify
from django.contrib.auth import login as auth_login, authenticate

from formtools.wizard.views import SessionWizardView

from django.contrib.auth.forms import AuthenticationForm

def buttonSelection(request):
    return render(request,'pickUserType.html')

def process_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    print(form_data)
    return form_data
    
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
class DoctorWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, '/doctor/'))
    template_name = "registration/signup.html"
    form_list = [SignUpForm,verify]
    
    def done(self, form_list, **kwargs):
        process_data(form_list)
        userCreate = form_list[0]

        addFields=userCreate.save(commit=False)
        addFields.verified=form_list[1].cleaned_data.get('verified')
        addFields.is_doctor=True

        addFields.save()
        username = userCreate.cleaned_data.get('username')
        raw_password = userCreate.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            auth_login(self.request, user)
        return redirect('home')
    
class UserWizard(SessionWizardView):
    template_name = "registration/signup.html"
    form_list = [SignUpForm]
    def done(self, form_list, **kwargs):
        process_data(form_list)
        form_list[0].save()
        userCreate = form_list[0]
        username = userCreate.cleaned_data.get('username')
        raw_password = userCreate.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            auth_login(self.request, user)
        return redirect('home')

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


""" def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user:
            auth_login(request,user)
            return redirect('home')
        else:
            return render(request,'registration/login.html',{'form':form})
    else:
        form = AuthenticationForm()
    return render(request,'registration/login.html',{'form':form}) """