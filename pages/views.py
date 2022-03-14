from django.shortcuts import redirect, render
from pages.calendar import Calendar
from .forms import BookAppointmentForm, ContactForm, MedicationForm, MessageForm, SignUpForm, UserProfileForm, Verify
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
from datetime import date, datetime
import pytz
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings

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
                messages.error(request,'User blocked',extra_tags='login')
                return redirect('login')
        else:
            messages.error(request,'username or password not correct',extra_tags='login')
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html',{'form':form})

def logout(request):
    auth_logout(request)
    messages.error(request, "You have successfully logged out.",extra_tags='login')
    return redirect('login')

def pickUserType(request):
    return render(request,'pickUserType.html')

@login_required
def process_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    #print(form_data)
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
    #print(message_id)
    parent = Messages.objects.get(id = message_id)
    if parent:
        reply = Messages.objects.create(text=request.POST['text'], receiver=parent.sender, sender=request.user, parent=parent)
    #print(parent)
    #print(reply)
    #print(request.POST)
    return redirect('messagesInbox')

@login_required
@require_http_methods(["POST"])
def send(request):
    send_message_form = MessageForm(request.POST or None,)
    #print(send_message_form)
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
    #print(user)
    if user:
        user.is_active = True
        user.save()
    return redirect('adminControls')

    
@login_required
@require_http_methods(["POST"])
def addMed(request):
    #print('Adding med')
    #print(request.user)
    #print(request.POST)
    med = MedicationForm(request.POST or None,)
    med.instance.user = request.user
    med.save()
    return redirect('medications')
    
def index(request):
    context = {}
    context['nmenu'] = 'home'
    tz = 'America/Vancouver'
    time_zone = pytz.timezone(tz)
    if request.user.is_authenticated:
        # Filter messages by if the user deleted from their view
        inbox = Messages.objects.filter(Q(sender=request.user)&Q(sender_deleted=False) | Q(receiver=request.user)&Q(receiver_deleted=False)).order_by("-time", "read")
        context['inbox'] = inbox
        unread_messages_count = Messages.objects.filter(Q(receiver=request.user) & Q(read=False)&Q(receiver_deleted=False)).count()
        context['unreadMessagesCount'] = unread_messages_count
        context['medications'] = Medications.objects.filter(user=request.user)
        edit_profile_form = UserProfileForm(instance=request.user)
        context['editProfileForm'] = edit_profile_form
        context['isPost'] = False
        if request.user.refresh_token !="":
            results = get_events(request.user.refresh_token,is_book_appointment=True)
            # Simply if there are no results you should return that otherwise you need to filter out by email and current date
            print(results)
            print("---------------")
            if len(results)==0:
                context['latestEventDay'] = 'No day'
                context['latestEventTime'] = 'No time'
                context['latestEventUser'] = "No user"
            else:
                # Get all the emails for every(active? and not current user) profile and cross check with events should be in ['attendee'] 
                    
                emails = [x.email for x in Profile.objects.exclude(Q(username=request.user))]
            
                print(emails)
                print("------------")
            
                after_date = [x for x in results if datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z') >=time_zone.localize(datetime.now())]
                print(after_date)
                print("---------------")
                with_out_attendee = []
                for e in after_date:
                    try:
                        if e['attendees'][0]['email'] in emails or e['attendees'][1]['email'] in emails:
                            with_out_attendee.append(e)
                    except KeyError:
                        pass
                if len(with_out_attendee)==0:
                    context['latestEventDay'] = 'No day'
                    context['latestEventTime'] = 'No time'
                    context['latestEventUser'] = "No user"
                else:

                    print(with_out_attendee)
                    print("---------------")
                    am_format = datetime.strptime(with_out_attendee[0]['start']['dateTime'][:-8].split('T')[1].split('-')[0], '%H:%M').strftime('%I:%M %p').lstrip('0')
                    print(am_format)
                    context['latestEventDay'] = datetime.strptime(with_out_attendee[0]['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z').strftime('%A, %B %d')
                    context['latestEventTime'] = am_format

                    # Figure out the user who messaged by using the email (Todo)
                    context['latestEventUser'] = 'User'

        if request.method=="POST":
            if 'editProfileForm' in request.POST:
                edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
                if edit_profile_form.is_valid():
                    edit_profile_form.save()
                    edit_profile_form = UserProfileForm(instance=request.user)
                    context['editProfileForm'] = edit_profile_form
                    context['isPost'] = False
                else:
                    context['isPost'] = True
                    context['editProfileForm'] = edit_profile_form
    else:
        contact_form = ContactForm()
        context['contactForm'] = contact_form
        if request.method=="POST":
            if 'contactForm' in request.POST:
                print('contact form')
                contact_form = ContactForm(request.POST)
                if contact_form.is_valid():
                    contact_form.save()
                    email_subject = f'New contact {contact_form.cleaned_data["email"]}: {contact_form.cleaned_data["subject"]}'
                    email_message = contact_form.cleaned_data['message']
                    send_mail(email_subject, email_message,'arundeepchohan2009@hotmail.com',['arundeepchohan2009@hotmail.com'])
  
    return render(request, 'home.html', context)

@login_required
def calendar(request):
    if request.user.refresh_token == "":
        return redirect('home')
    context = {}  
    context['nmenu'] = 'calendar'
    results = get_events(request.user.refresh_token,is_book_appointment=False)
    d = datetime.now()
    #print(d)
    cal = Calendar(d.year, d.month,d.day,d,request.user)
    html_cal = cal.formatmonth(request,results, withyear=True,is_book_appointment=False)
    #print(mark_safe(html_cal))
    context['personalCalendar'] = mark_safe(html_cal)
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
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form

    return render(request, 'home.html', context)

@login_required
def messagesSend(request):
    context = {}
    context['nmenu'] = 'messagesSend'
    send_message_form = MessageForm()
    if request.user.is_staff:
        send_message_form .fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True))
    elif request.user.verified:
        send_message_form.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True))           
    else:
        send_message_form.fields['receiver'].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True)|Q(is_staff=True)|Q(username=request.user))
    context['sendMessageForm'] = send_message_form 
    edit_profile_form = UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form= UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False

            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form
    return render(request, 'home.html', context)

@login_required
def messagesInbox(request):
    context = {}
    context['nmenu'] = 'messagesInbox'
    inbox = Messages.objects.filter(Q(sender=request.user)&Q(sender_deleted=False) | Q(receiver=request.user)&Q(receiver_deleted=False)).order_by("-time", "read")
    context['inbox'] = inbox
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

            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form

    return render(request, 'home.html', context)

@login_required
def documents(request):
    context={}
    context['nmenu'] = 'documents'
    edit_profile_form = UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form= UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False

            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form

    return render(request, 'home.html', context)

@login_required
def medications(request):
    context={}  
    context['nmenu'] = 'medications'
    context['medicationForm'] = MedicationForm()
    context['medications'] = Medications.objects.filter(user=request.user)
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

            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form

    return render(request, 'home.html', context)

@login_required
def adminControls(request):
    if request.user.is_staff is not True:
        return redirect('home')
    context={}
    context['nmenu'] = 'adminControls'
    # Only admins needs to know inactive users
    context['allInactiveDoctors'] = Profile.objects.filter(Q(is_active=False)&Q(is_doctor=True))
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
            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form

    return render(request, 'home.html', context)

@login_required
def bookAppointment(request):
    # Make a checks to see if it's a user and not doctor, add a check for if it has request.user.refresh_token(Todo)
    if request.user.is_staff is True or request.user.is_doctor is True:
        return redirect('home')
    context = {}
    context['nmenu'] = 'bookAppointment'
    book_appointment = BookAppointmentForm()
    # Make sure I get active doctors and doctors who have a refresh_token
    book_appointment.fields['doctors'].queryset = Profile.objects.filter(Q(is_active=True)&Q(is_doctor=True)&~Q(refresh_token=""))
    context['bookAppointment'] = book_appointment
    edit_profile_form= UserProfileForm(instance=request.user)
    context['editProfileForm'] = edit_profile_form
    if request.method=="POST":
        if 'editProfileForm' in request.POST:
            edit_profile_form= UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                edit_profile_form = UserProfileForm(instance=request.user)
                context['editProfileForm'] = edit_profile_form
                context['isPost'] = False

            else:
                context['isPost'] = True
                context['editProfileForm'] = edit_profile_form

        if 'bookAppointment' in request.POST:
            d = datetime.now()
            #print(d)
            book_appointment = BookAppointmentForm(request.POST)
            if book_appointment.is_valid():
                #print(request.POST['doctors'])
                #print(int(request.POST['doctors'])-1)
                # What if the doctor gets deleted?
                try:
                    # This associates the user with the dropdown selection
                    name = Profile.objects.all()[int(request.POST['doctors'])-1]
                    #print(name)
                    user = Profile.objects.get(username=name)
                    if user:
                        #print(user,user.refresh_token)
                        #results = test_calendar()
                        results = get_events(user.refresh_token,is_book_appointment=True)
                        cal = Calendar(d.year,d.month,d.day,d,user.username)
                        html_cal = cal.formatmonth(request,results,withyear=True,is_book_appointment=True)
                        context['calendar'] = mark_safe(html_cal)
                except IndexError:
                    messages.error(request,'Booking failed',extra_tags='bookAppointment')
                    return redirect('bookAppointment')

        
    return render(request, 'home.html', context)

@login_required
@require_http_methods(["POST"])
def addAppointment(request,username,start):
    #print('Add appointment')
    #print(request.user)
    doctor = Profile.objects.get(username=username)
    if doctor:
        #print(doctor)
        #print(start)
        tz = pytz.timezone('America/Vancouver')
        today = datetime.now(tz)
        time_slot = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
        #print(today,time_slot)
        #print(type(today),type(time_slot))
        #print(time_slot>=today)

        # Make a certain time before appointment let's say 1 hour before
        # What if the doctor added events between the page reload?
        results = get_events(doctor.refresh_token,is_book_appointment=True)
        events_per_day = list(filter(lambda x: datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z') == time_slot, results))
        # print(len(events_per_day))
        # Check if time_slot is in results
        if len(events_per_day)>=1:
            messages.error(request,'Booked',extra_tags='bookAppointment')
        elif time_slot >= today:
            add_appointment(request.user,doctor,start)
        else:
            messages.error(request,'Booking failed',extra_tags='bookAppointment')
    else:
        messages.error(request,'Booking failed',extra_tags='bookAppointment')

    return redirect('bookAppointment')