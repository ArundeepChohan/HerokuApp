from django.http.response import HttpResponse
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
    context = {'is_post': False}
    if request.method == "POST":
        context['is_post'] = True
        form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home') 
    else:
        form = UserProfileForm(instance=request.user)
    context['form']= form
    return render(request, "home.html", context)