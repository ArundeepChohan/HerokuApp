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
from pages.googleCalendarAPI import add_appointment, test_calendar, get_events
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
        user_create = form_list[0]
        user_create.save()
        username = user_create.cleaned_data.get('username')
        raw_password = user_create.cleaned_data.get('password1')
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
        user_create = form_list[0]
        username = user_create.cleaned_data.get('username')
        raw_password = user_create.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        if user:
            auth_login(self.request, user)
        return redirect('home')

@login_required
@require_http_methods(["POST"])
def reply(request,message_id):
    print(message_id)
    parent = Messages.objects.get(id=message_id)
    reply = Messages.objects.create(text=request.POST['text'], receiver=parent.sender, sender=request.user, parent=parent)
    print(parent)
    print(reply)
    print(request.POST)
    return redirect('messagesInbox')

@login_required
@require_http_methods(["POST"])
def send(request):
    send_message_form = MessageForm(request.POST or None,)
    print(send_message_form )
    if send_message_form.is_valid(): 
        send_message_form_user = send_message_form.save(commit=False)
        send_message_form_user.sender = request.user
        send_message_form_user.save()
    return redirect('messagesSend')

@login_required
@require_http_methods(["POST"])
def delete(request,message_id):
    #Only remove the message if both people want it removed or if the send and receiver are the same person
    data_to_be_deleted = Messages.objects.get(id = message_id)
    
    if data_to_be_deleted.sender ==request.user and data_to_be_deleted.receiver==request.user:
        data_to_be_deleted.delete()
        return redirect('messagesInbox')
    else:
        if data_to_be_deleted.sender==request.user:
            data_to_be_deleted.sender_deleted=True
            data_to_be_deleted.save()
        else:
            data_to_be_deleted.receiver_deleted=True
            data_to_be_deleted.save()

    data_to_be_deleted = Messages.objects.get(id = message_id)
    if data_to_be_deleted.sender_deleted and data_to_be_deleted.receiver_deleted:
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
    
def index(request):
    context={}
    context['nmenu']='home'
    
    if request.method=="POST":
        #Filter messages by if the user deleted from their view
        inbox = Messages.objects.filter(Q(sender=request.user)&Q(sender_deleted=False) | Q(receiver=request.user)&Q(receiver_deleted=False)).order_by("-time", "read")
        context['inbox'] = inbox
        unread_messages_count = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)&Q(receiver_deleted=False)).count()
        context['unreadMessagesCount'] = unread_messages_count
        edit_profile_form = UserProfileForm(instance=request.user)
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)
    else:
        if request.user.is_authenticated:
            inbox = Messages.objects.filter(Q(sender=request.user)&Q(sender_deleted=False) | Q(receiver=request.user)&Q(receiver_deleted=False)).order_by("-time", "read")
            context['inbox'] = inbox
            unread_messages_count = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)&Q(receiver_deleted=False)).count()
            context['unreadMessagesCount'] = unread_messages_count
            edit_profile_form = UserProfileForm(instance=request.user)
            context['editProfileForm'] = edit_profile_form
            context['isPost'] = False
    return render(request, 'home.html', context)

@login_required
def calendar(request):
    context={}  
    results = get_events(request.user.refresh_token,is_book_appointment=False)
    d = date.today()
    print(d)
    cal = Calendar(d.year, d.month)
    html_cal = cal.formatmonth(results, withyear=True,is_book_appointment=False)
    print(mark_safe(html_cal))
    context['personalCalendar'] = mark_safe(html_cal)
    context['nmenu'] = 'calendar'
    edit_profile_form = UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)

    return render(request, 'home.html', context)

@login_required
def messagesSend(request):
    context={}
    edit_profile_form = UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    send_message_form = MessageForm()
    if request.user.is_staff:
        send_message_form .fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True))
    elif request.user.verified:
        send_message_form.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True))           
    else:
        send_message_form.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True)|Q(is_staff=True)|Q(username=request.user))
    context['sendMessageForm'] = send_message_form 
    context['nmenu'] = 'messagesSend'
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form= UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)

    return render(request, 'home.html', context)

@login_required
def messagesInbox(request):
    context={}
    edit_profile_form= UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    inbox = Messages.objects.filter(Q(sender=request.user)&Q(sender_deleted=False) | Q(receiver=request.user)&Q(receiver_deleted=False)).order_by("-time", "read")
    context['inbox'] = inbox
    context['nmenu'] = 'messagesInbox'
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)
    return render(request, 'home.html', context)

@login_required
def documents(request):
    context={}
    edit_profile_form = UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    context['nmenu'] = 'documents'
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form= UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)
    return render(request, 'home.html', context)

@login_required
def medications(request):
    context={}  
    context['nmenu'] = 'medications'
    edit_profile_form = UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    context['medicationForm'] = MedicationForm()
    context['medications']= Medications.objects.filter(user=request.user)
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)

    return render(request, 'home.html', context)

@login_required
def adminControls(request):
    context={}
    # Only admins needs to know inactive users
    context['allInactiveDoctors'] = Profile.objects.filter(Q(is_active=False)&Q(is_doctor=True))
    context['nmenu'] = 'adminControls'
    edit_profile_form= UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)
        
    return render(request, 'home.html', context)

@login_required
def bookAppointment(request):
    context={}
    edit_profile_form= UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    book_appointment = BookAppointmentForm()
    # Make sure I get active doctors and doctors who have a refresh_token
    book_appointment.fields['doctors'].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True)&~Q(refresh_token=""))
    context['bookAppointment'] = book_appointment
    context['nmenu'] = 'bookAppointment'
   
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form= UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False
                return render(request, "home.html", context)
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
                return render(request, "home.html", context)
        if 'bookAppointment' in request.POST:
            d = date.today()
            print(d)
            book_appointment = BookAppointmentForm(request.POST)
            if book_appointment.is_valid():
                print(request.POST['doctors'])
                print(int(request.POST['doctors'])-1)
                # This associates the user with the dropdown selection
                name = Profile.objects.all()[int(request.POST['doctors'])-1]
                print(name)
                user = Profile.objects.get(username=name)
                if user:
                    print(user,user.refresh_token)
                    #results = test_calendar()
                    results = get_events(user.refresh_token,is_book_appointment=True)
                    cal = Calendar(d.year, d.month,user.username)
                    html_cal = cal.formatmonth(results,withyear=True,is_book_appointment=True)
                    context['calendar'] = mark_safe(html_cal)
            return render(request, 'home.html', context)
        
    return render(request, 'home.html', context)

@login_required
def addAppointment(request,username,start):
    print('add appointment')
    print(request.user)
    doctor = Profile.objects.get(username=username)
    print(doctor)
    print(start)
    add_appointment(request.user,doctor,start)
    return redirect('bookAppointment')