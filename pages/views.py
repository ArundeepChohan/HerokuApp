from django.shortcuts import redirect, render
from .forms import UserProfileForm
from .models import Profile

def index(request):
    context = {}
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("avatar")
            obj = Profile.objects.create(
                                 avatar = img
                                 )
            obj.save(commit=False)
            print(obj)
            return redirect(request, "home.html", obj)

    else:
        form = UserProfileForm()
    context['form']= form
    return render(request, "home.html", context)