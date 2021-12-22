from django.shortcuts import redirect, render
from .forms import UserProfileForm
from .models import Profile

def index(request):
    context = {}
    if request.method == "POST":
        print(request.POST)
        form = UserProfileForm(request.POST or None, request.FILES or None,instance=request.user)
        if form.is_valid():
            """ 
            img = form.cleaned_data.get("avatar")
            print(img)
            print(form.cleaned_data.get('username'))
            print(request.user)
            obj, created = Profile.objects.update_or_create(
                username=form.cleaned_data.get('username'),
                defaults={'avatar': img},
            )
            obj.save()
            print(obj)
            """
            form.save()
            return redirect('home') 
    else:
        form = UserProfileForm()
    context['form']= form
    return render(request, "home.html", context)