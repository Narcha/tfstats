from django.shortcuts import redirect
from django.core.handlers.wsgi import WSGIRequest
from steam_api.steamid import resolve_steamid_or_profile_link
from tfstats.errors import SteamAPIError

# Create your views here.
def search(request: WSGIRequest):
    query = request.GET["query"]
    try:
        resolved_id = resolve_steamid_or_profile_link(query)
    except SteamAPIError:
        return redirect("/")
    if resolved_id is None:
        return redirect("/")
    return redirect("/profiles/" + str(resolved_id))