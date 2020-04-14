from django.shortcuts import redirect
from django.utils.http import urlencode
from django.core.handlers.wsgi import WSGIRequest
from steam_api.models import PlayerProfile

# Create your views here.
def lits(request):
    server_name = request.scheme + "://" + request.META['HTTP_HOST']
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
    steamid = request.GET.get("openid.claimed_id").split("/")[-1]
    profile = PlayerProfile()
    profile.get_by_steamid(steamid)
    request.session["profile"] = {
        "steamid": profile.steamid,
        "displayname": profile.displayname,
        "profile_url": profile.profile_url,
        "timecreated": profile.timecreated.timestamp(),
        "avatar_url_small": profile.avatar_url_small,
        "avatar_url_medium": profile.avatar_url_medium,
        "avatar_url_full": profile.avatar_url_full,
    }
    return redirect("/")