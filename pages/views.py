from django.shortcuts import render
from .forms import UserProfileForm

def index(request):
    return render(request,'home.html')
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'home.html', {'form': form, 'img_obj': img_obj})
    else:
        form = UserProfileForm()
    return render(request, 'home.html', {'form': form})