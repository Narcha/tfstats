import requests
import json
import re
import tfstats.settings
import steam_api
from tfstats.errors import InvalidSteamIDError, SteamAPIError

def validate_steamid(steamid):
    try:
        steamid_int = int(steamid)
    except ValueError:
        return False

    # miximum and minimum steamID possible
    if 76561197960265729 < steamid_int < 76561202255233023:
        return True
    else:
        return False

def resolve_vanity_url_fragment(url_frag):
    response = requests.get(steam_api.STEAM_API_RESOLVEVANITYURL_URL % (tfstats.settings.STEAM_API_KEY, url_frag))
    if response.status_code == 500:
        return None
    if response.status_code != 200:
        raise SteamAPIError(response.status_code)
    try:
        decoded_json = json.loads(response.text)["response"]
    except (KeyError, json.decoder.JSONDecodeError):
        return None
    if not decoded_json["success"] == 1:
        return None
    else:
        return int(decoded_json["steamid"])

def resolve_steamid_or_profile_link(query:str):
    """takes a possible SteamID, a vanity URL segment, or a complete profile url,
    and returns the corresponding SteamID as an int."""

    re_vanity = re.compile("steamcommunity.com\/id\/([\w-]+)")
    re_steamid = re.compile("steamcommunity.com\/profiles\/(\d+)")
    
    # check if query is an "id" link
    match = re_vanity.search(query)
    if match:
        return resolve_vanity_url_fragment(match.group(1))
    
    # check if query is a "profile" link
    match = re_steamid.search(query)
    if match:
        if validate_steamid(match.group(1)):
            return match.group(1)
        else:
            return None

    # query is not a profile link. It's either an url fragment or a SteamID64.
    # check if it's a SteamID
    if validate_steamid(query):
        return int(query)
    else:
        # now, query is either an url fragment or invalid.
        return resolve_vanity_url_fragment(query)