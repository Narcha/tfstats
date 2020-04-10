from django.shortcuts import redirect
from django.utils.http import urlencode
from django.core.handlers.wsgi import WSGIRequest

# Create your views here.
def lits(request):
    server_name = request.scheme + "://" + request.META['SERVER_NAME']
    RETURN_TO = server_name + "/login/return"
    BASE_URL = "https://steamcommunity.com/openid/login?"
    QUERY_PARAMS = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": RETURN_TO,
        "openid.realm": server_name,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    
    login_url = BASE_URL + urlencode(QUERY_PARAMS)

    return redirect(login_url)

def return_url(request: WSGIRequest):
    print(request.get_full_path())
    print(request.GET)
    print(request.GET.keys())
    request.session["steamid"] = request.GET.get("openid.claimed_id").split("/")[-1]
    return redirect("/")