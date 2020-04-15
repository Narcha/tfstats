from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from steam_api.models import PlayerStat, PlayerProfile
from tfstats.errors import InvalidSteamIDError, SteamAPIError
from steam_api.steamid import resolve_steamid_or_profile_link

def index(request):
    return render(request, "profiles_index.html")

def profile_not_found(request):
    return render(request, "profile_not_found.html")

def profile(request, steamid):
    try:
        resolved_id = resolve_steamid_or_profile_link(steamid)
    except SteamAPIError:
        return index(request)

    if resolved_id is None:
        raise InvalidSteamIDError()
    
    print("resolved id is %s"%resolved_id)

    # Check if we have records for the given steamID already
    try:
        db_record = PlayerStat.objects.get(steamid=resolved_id)
    except PlayerStat.DoesNotExist:
        db_record = None
    print("looked up records for %d, found %s"% (resolved_id, db_record))

    playerstats = None

    if db_record is not None:
        # update existing record if that entry is older than five minutes
        if timezone.now() - db_record.timestamp > timezone.timedelta(minutes=5):
            db_record.get_by_steamid(resolved_id)
        playerstats = db_record
    else:
        # create new record
        playerstats = PlayerStat()
        playerstats.get_by_steamid(resolved_id)


    # Serve either the new record or an old one, given that it's not older than five minutes
    return render(request, 'profile.html', {"playerstats": playerstats})
