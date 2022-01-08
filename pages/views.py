

from django.shortcuts import redirect, render
from .forms import MessageForm, SignUpForm, UserProfileForm, verify
from django.contrib.auth import login as auth_login, authenticate

from formtools.wizard.views import SessionWizardView

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request,'User blocked')
                return redirect('login')
        else:
            messages.error(request,'username or password not correct')
            return redirect('login')

    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html',{'form':form})

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
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'doctor'))
    template_name = "registration/signup.html"
    form_list = [SignUpForm,verify]
    
    def done(self, form_list, **kwargs):
        process_data(form_list)
        userCreate = form_list[0]
        userCreate.save()
        username = userCreate.cleaned_data.get('username')
        raw_password = userCreate.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            user.verified=form_list[1].cleaned_data.get('verified')
            user.is_doctor=True
            user.is_active=False
            user.save()
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

##Rework this to only show forms on log in and post method
from .models import Messages
from django.db.models.query_utils import Q
def index(request):
    context = {'is_post': False}
    sendMessageForm = MessageForm()
    editProfileForm = UserProfileForm()
    if request.method == "POST":
        Inbox = Messages.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by("-time", "read")
        context['Inbox'] = Inbox
        unreadMessagesCount = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)).count()
        context['unreadMessagesCount'] = unreadMessagesCount
        if 'editProfileForm' in request.POST:          
            context['is_post'] = True
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                return redirect('home') 
        elif 'sendMessage' in request.POST:
            sendMessageForm = MessageForm(request.POST or None,)
            if sendMessageForm.is_valid(): 
                sendMessageFormUser =  sendMessageForm.save(commit=False)
                sendMessageFormUser.sender = request.user
                sendMessageFormUser.save()
                unreadMessagesCount = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)).count()
                context['unreadMessagesCount'] = unreadMessagesCount
                return redirect('home')
    else:
        # Checks if user is logged out or in and passes to form
        if request.user.is_authenticated:
            editProfileForm= UserProfileForm(instance=request.user)
            Inbox = Messages.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by("-time", "read")
            context['Inbox'] = Inbox
            unreadMessagesCount=Messages.objects.filter(Q(receiver=request.user) & Q(read=False)).count()
            context['unreadMessagesCount'] = unreadMessagesCount    
        else:
            editProfileForm = UserProfileForm()

    context['editProfileForm'] = editProfileForm
    context['sendMessageForm'] = sendMessageForm
    return render(request, "home.html", context)