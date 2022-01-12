from django.shortcuts import redirect, render
from .forms import MessageForm, SignUpForm, UserProfileForm, Verify
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
    form_list = [SignUpForm,Verify]
    
    def done(self, form_list, **kwargs):
        process_data(form_list)
        userCreate = form_list[0]
        userCreate.save()
        username = userCreate.cleaned_data.get('username')
        raw_password = userCreate.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            user.verified = form_list[1].cleaned_data.get('verified')
            user.is_doctor= True
            user.is_active = False
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

from django.views.decorators.http import require_http_methods
@require_http_methods(["POST"])
def reply(request,messageID):
    print(messageID)
    parent = Messages.objects.get(id=messageID)
    reply = Messages.objects.create(text=request.POST['text'], receiver=parent.sender, sender=request.user, parent=parent)
    print(parent)
    print(reply)
    print(request.POST)
    return redirect('home')

@require_http_methods(["POST"])
def send(request):
    sendMessageForm = MessageForm(request.POST or None,)
    print(sendMessageForm)
    if sendMessageForm.is_valid(): 
        sendMessageFormUser = sendMessageForm.save(commit=False)
        sendMessageFormUser.sender = request.user
        sendMessageFormUser.save()
    return redirect('home')

@require_http_methods(["POST"])
def delete(request,messageID):
    data_to_be_deleted = Messages.objects.get(id = messageID)
    data_to_be_deleted.delete()
    return redirect('home')

@require_http_methods(["POST"])
def activate(request,username):
    user = Profile.objects.get(username=username)
    print(user)
    user.is_active = True
    user.save()

    return redirect('home')

##Rework this to only show forms while logged in and post method
from .models import Messages, Profile
from django.db.models.query_utils import Q
from pages.googleCalendarAPI import test_calendar
def index(request):
    context = {'is_post': False}
    sendMessageForm = MessageForm()
    editProfileForm = UserProfileForm()
    results = test_calendar()
    context = {"results": results}
    if request.method == "POST":
        if 'editProfileForm' in request.POST:          
            context['is_post'] = True
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                return redirect('home') 
    else:
        # Checks if user is logged out or in and passes to form
        if request.user.is_authenticated:
            context['allInactiveDoctors'] = Profile.objects.filter(Q(is_active=False)&Q(is_doctor=True))
            editProfileForm = UserProfileForm(instance=request.user)
            Inbox = Messages.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by("-time", "read")
            context['Inbox'] = Inbox
            unreadMessagesCount = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)).count()
            context['unreadMessagesCount'] = unreadMessagesCount
            if request.user.is_staff:
                sendMessageForm.fields["receiver"].queryset = Profile.objects.filter(Q(is_active=True))
            elif request.user.verified !='':
                sendMessageForm.fields["receiver"].queryset = Profile.objects.filter(Q(is_active=True))           
            else:
                sendMessageForm.fields["receiver"].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True)|Q(is_staff=True))

    context['editProfileForm'] = editProfileForm
    context['sendMessageForm'] = sendMessageForm
    return render(request, "home.html", context)