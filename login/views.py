from django.shortcuts import redirect
from django.utils.http import urlencode
from django.core.handlers.wsgi import WSGIRequest
from steam_api.models import PlayerProfile
import re, requests


def ValidateResults(get_params):
    validationArgs = {
        'openid.sig' : get_params['openid.sig'],
        'openid.ns': get_params ['openid.ns']
    }
    signedArgs = get_params['openid.signed'].split(',')

    for item in signedArgs:
        itemArg = 'openid.%s' % item
        validationArgs[itemArg] = get_params[itemArg]

    validationArgs['openid.mode'] = 'check_authentication'

    response = requests.get('https://steamcommunity.com/openid/login', params=validationArgs)

    if re.search('is_valid:true', response.text):
        matchedID = re.search('https://steamcommunity.com/openid/id/(\d+)', get_params['openid.claimed_id'])
        if matchedID and matchedID.group(1):
            return matchedID.group(1)
        else:
            return False
    else:
        return False

def lits(request):
    server_name = request.scheme + "://" + request.META['HTTP_HOST']
    RETURN_TO = server_name + "/login/return/"
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
    steamid = ValidateResults(request.GET)
    if steamid == False:
        return redirect("/")
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