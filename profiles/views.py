from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from steam_api.models import PlayerStat, PlayerProfile, validate_steamid
import tfstats.errors

def index(request):
    return render(request, 'profiles_index.html', {"page_name": "Profiles"})

def profile(request, steamid):
    if not validate_steamid(steamid):
        return invalid_id(request, steamid)

    # Check if we have records for the given steamID already
    try:
        db_record = PlayerStat.objects.get(steamid=steamid)
    except PlayerStat.DoesNotExist:
        db_record = None
    print("looked up records for %d, found %s"% (steamid, db_record))

    playerstats = None

    if db_record is not None:
        # update existing record if that entry is older than five minutes
        if timezone.now() - db_record.timestamp > timezone.timedelta(minutes=5):
            db_record.get_by_steamid(steamid)
        playerstats = db_record
    else:
        # create new record
        playerstats = PlayerStat()
        playerstats.get_by_steamid(steamid)


    # Serve either the new record or an old one, given that it's not older than five minutes
    return render(request, 'profile.html', {"page_name": "Profile", "playerstats": playerstats})

def invalid_id(request, steamid):
    return HttpResponseNotFound("Invalid SteamID (%s)"%steamid)
