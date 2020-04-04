from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the profiles index.")

def profile(request, steamid):
    return render(request, 'profiles.html')
    # return HttpResponse(str(steamid))