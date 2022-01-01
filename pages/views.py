
from django.shortcuts import redirect, render
from .forms import SignUpForm, UserProfileForm
from django.contrib.auth import login, authenticate

from formtools.wizard.views import SessionWizardView

def show_message_form_condition(wizard):
    # try to get the cleaned data of step 1
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    # check if the field isDoctor was checked.
    #print(cleaned_data.get('is_doctor')== False)
    return cleaned_data.get('is_doctor')== False

def process_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    print(form_data)
    return form_data

class ContactWizard(SessionWizardView):

    def done(self, form_list, **kwargs):
        process_data(form_list)
        return redirect('home')

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