from django.shortcuts import redirect, render
from .forms import SignUpForm, UserProfileForm
from django.contrib.auth import login, authenticate

def signup(request):
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
    return render(request, 'registration/signup.html', {'form': form})

def index(request):
    context = {}
    if request.method == "POST":
        print(request.POST)
        form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home') 
    else:
        form = UserProfileForm()
    context['form']= form
    context['active_tab']='tab1'
    return render(request, "home.html", context)