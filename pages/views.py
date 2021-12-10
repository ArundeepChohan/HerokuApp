from django.shortcuts import render
from django.contrib.auth.decorators import login_required. 

@login_required
def index(request):
    # now the index function renders the home page
    return render(request,'home.html') 