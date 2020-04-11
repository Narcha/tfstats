from django.shortcuts import redirect
from django.core.handlers.wsgi import WSGIRequest
from steam_api.steamid import resolve_steamid_or_profile_link

# Create your views here.
def search(request: WSGIRequest):
    query = request.GET["query"]
    resolved_id = resolve_steamid_or_profile_link(query)
    return redirect("/profiles/" + str(resolved_id))