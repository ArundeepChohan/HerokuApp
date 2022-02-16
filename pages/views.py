from django.shortcuts import redirect, render
from pages.calendar import Calendar
from .forms import BookAppointmentForm, MedicationForm, MessageForm, SignUpForm, UserProfileForm, Verify
from django.contrib.auth import login as auth_login, logout as auth_logout,authenticate
from formtools.wizard.views import SessionWizardView
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Medications, Messages, Profile
from django.db.models.query_utils import Q
from pages.googleCalendarAPI import test_calendar, get_events
from django.utils.safestring import mark_safe
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import date
from django.views.decorators.http import require_http_methods

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

def logout(request):
    auth_logout(request)
    messages.error(request, "You have successfully logged out.")
    return redirect('login')

def pickUserType(request):
    return render(request,'pickUserType.html')

@login_required
def process_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    print(form_data)
    return form_data
    
class DoctorWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'doctor'))
    template_name = "registration/signup.html"
    form_list = [SignUpForm,Verify]
    
    def done(self, form_list, **kwargs):
        #process_data(form_list)
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
        #process_data(form_list)
        form_list[0].save()
        userCreate = form_list[0]
        username = userCreate.cleaned_data.get('username')
        raw_password = userCreate.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            auth_login(self.request, user)
        return redirect('home')

@login_required
@require_http_methods(["POST"])
def reply(request,messageID):
    print(messageID)
    parent = Messages.objects.get(id=messageID)
    reply = Messages.objects.create(text=request.POST['text'], receiver=parent.sender, sender=request.user, parent=parent)
    print(parent)
    print(reply)
    print(request.POST)
    return redirect('messagesInbox')

@login_required
@require_http_methods(["POST"])
def send(request):
    sendMessageForm = MessageForm(request.POST or None,)
    print(sendMessageForm)
    if sendMessageForm.is_valid(): 
        sendMessageFormUser = sendMessageForm.save(commit=False)
        sendMessageFormUser.sender = request.user
        sendMessageFormUser.save()
    return redirect('messagesSend')

@login_required
@require_http_methods(["POST"])
def delete(request,messageID):
    #Only remove the message if both people want it removed or if the send and receiver are the same person
    data_to_be_deleted = Messages.objects.get(id = messageID)
    
    if data_to_be_deleted.sender ==request.user and data_to_be_deleted.receiver==request.user:
        data_to_be_deleted.delete()
        return redirect('messagesInbox')
    else:
        if data_to_be_deleted.sender==request.user:
            data_to_be_deleted.senderDeleted=True
            data_to_be_deleted.save()
        else:
            data_to_be_deleted.receiverDeleted=True
            data_to_be_deleted.save()

    data_to_be_deleted = Messages.objects.get(id = messageID)
    if data_to_be_deleted.senderDeleted and data_to_be_deleted.receiverDeleted:
        data_to_be_deleted.delete()
    return redirect('messagesInbox')

@login_required
@require_http_methods(["POST"])
def activate(request,username):
    user = Profile.objects.get(username=username)
    print(user)
    if user:
        user.is_active = True
        user.save()
    return redirect('adminControls')

    
@login_required
@require_http_methods(["POST"])
def addMed(request):
    print('Adding med')
    print(request.user)
    print(request.POST)
    med = MedicationForm(request.POST or None,)
    med.instance.user = request.user
    med.save()
    return redirect('medications')
    
#Filter messages by if the user deleted from their view
def index(request):
    context={}
    context['nmenu']='home'
    
    if request.method=="POST":
        Inbox = Messages.objects.filter(Q(sender=request.user)&Q(senderDeleted=False) | Q(receiver=request.user)&Q(receiverDeleted=False)).order_by("-time", "read")
        context['Inbox'] = Inbox
        unreadMessagesCount = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)&Q(receiverDeleted=False)).count()
        context['unreadMessagesCount'] = unreadMessagesCount
        editProfileForm = UserProfileForm(instance=request.user)
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)
    else:
        if request.user.is_authenticated:
            Inbox = Messages.objects.filter(Q(sender=request.user)&Q(senderDeleted=False) | Q(receiver=request.user)&Q(receiverDeleted=False)).order_by("-time", "read")
            context['Inbox'] = Inbox
            unreadMessagesCount = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)&Q(receiverDeleted=False)).count()
            context['unreadMessagesCount'] = unreadMessagesCount
            editProfileForm = UserProfileForm(instance=request.user)
            context['editProfileForm'] = editProfileForm
            context['is_post'] = False
    return render(request, 'home.html', context)

@login_required
def calendar(request):
    context={}  
    results = get_events(request)
    #context['results'] = results
    d = date.today()
    print(d)
    cal = Calendar(d.year, d.month)
    html_cal = cal.formatmonth(results, withyear=True)
    print(mark_safe(html_cal))
    context['personal_calendar'] = mark_safe(html_cal)
    context['nmenu'] = 'calendar'
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)

    return render(request, 'home.html', context)

@login_required
def messagesSend(request):
    context={}
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    sendMessageForm = MessageForm()
    if request.user.is_staff:
        sendMessageForm.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True))
    elif request.user.verified:
        sendMessageForm.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True))           
    else:
        # Not getting self need to rework remove when fixed maybe username=request.user
        sendMessageForm.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True)|Q(is_staff=True)|Q(username=request.user))
    context['sendMessageForm'] = sendMessageForm
    context['nmenu'] = 'messagesSend'
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)

    return render(request, 'home.html', context)

@login_required
def messagesInbox(request):
    context={}
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    Inbox = Messages.objects.filter(Q(sender=request.user)&Q(senderDeleted=False) | Q(receiver=request.user)&Q(receiverDeleted=False)).order_by("-time", "read")
    context['Inbox'] = Inbox
    context['nmenu'] = 'messagesInbox'
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)
    return render(request, 'home.html', context)

@login_required
def documents(request):
    context={}
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    context['nmenu'] = 'documents'
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)
    return render(request, 'home.html', context)

@login_required
def medications(request):
    context={}  
    context['nmenu'] = 'medications'
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    context['medicationForm'] = MedicationForm()
    context['medications']= Medications.objects.filter(user=request.user)
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)

    return render(request, 'home.html', context)

@login_required
def adminControls(request):
    context={}
    # Only admins needs to know inactive users
    context['allInactiveDoctors'] = Profile.objects.filter(Q(is_active=False)&Q(is_doctor=True))
    context['nmenu'] = 'adminControls'
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)
        
    return render(request, 'home.html', context)

@login_required
def bookAppointment(request):
    context={}
    editProfileForm = UserProfileForm(instance=request.user)
    context['editProfileForm'] = editProfileForm
    # Only bookAppointment if it's a user check is unnecessary if I check from the front end.
    bookAppointment = BookAppointmentForm()
    # Make sure I get active doctors and doctors who have a refresh_token
    bookAppointment.fields['doctors'].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True))
    context['bookAppointment'] = bookAppointment 
    context['nmenu'] = 'bookAppointment'
   
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            editProfileForm = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if editProfileForm.is_valid():
                editProfileForm.save()
                editProfileForm = UserProfileForm(instance=request.user)
                context['editProfileForm'] = editProfileForm
                context['is_post'] = False
                return render(request, "home.html", context)
            else:
                context['is_post'] = True
                context['editProfileForm'] = editProfileForm
                return render(request, "home.html", context)
        if 'bookAppointment' in request.POST:
            d = date.today()
            print(d)
            results = test_calendar()
            cal = Calendar(d.year, d.month)
            html_cal = cal.formatmonth(results, withyear=True)
            context['calendar'] = mark_safe(html_cal)
            return render(request, 'home.html', context)
        
    return render(request, 'home.html', context)

