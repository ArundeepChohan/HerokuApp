from django.shortcuts import render

def index(request):
    # now the index function renders the home page
    return render(request,'home.html') 