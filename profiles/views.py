from math import floor
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from steam_api.models import Player
from steam_api.steamid import resolve_steamid_or_profile_link
from tfstats.errors import InvalidSteamIDError, SteamAPIError

def index(request):
    return render(request, "profiles_index.html")

def profile_not_found(request):
    return render(request, "profile_not_found.html")

def profile(request, steamid):
    try:
        resolved_id = resolve_steamid_or_profile_link(steamid)
    except SteamAPIError:
        return redirect("/", {"message": "Steam API not reachable"})

    if resolved_id is None:
        return redirect("/")

    # Check if we have records for the given steamID already
    try:
        db_record = Player.objects.get(steamid=resolved_id)
    except Player.DoesNotExist:
        db_record = None

    playerstats = None

    if db_record is not None:
        # update existing record if that entry is older than five minutes
        if timezone.now() - db_record.updated_at > timezone.timedelta(minutes=5):
            db_record.from_steamid(resolved_id)
        playerstats = db_record
    else:
        # create new record
        playerstats = Player()
        playerstats.from_steamid(resolved_id)

    if playerstats.profile_level < 100:
        profile_level_class = floor(playerstats.profile_level / 10) * 10
    else:
        profile_level_class = floor(playerstats.profile_level / 100) * 100
    return render(request, 'profile.html', {
        "profile": playerstats,
        "profile_level_class": profile_level_class,
    })
