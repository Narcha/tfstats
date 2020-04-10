from django.shortcuts import redirect

STEAM_LOGIN_URL = "https://steamcommunity.com/oauth/login?response_type=token&client_id=client_id_here&state=whatever_you_want"

# Create your views here.
def lits(request):
    return redirect(STEAM_LOGIN_URL)