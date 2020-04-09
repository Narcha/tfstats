from django.shortcuts import render
from django.http import HttpResponseNotFound


def index(request):
    return render(request, 'profiles_index.html')

def profile(request, steamid):
    return render(request, 'profile.html', {"page_name": "Profile", "steamid": steamid})

def invalid_id(request, steamid):
    return HttpResponseNotFound("Invalid SteamID")