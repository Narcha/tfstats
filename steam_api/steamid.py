import steam_api
import requests
import json
import tfstats.settings
from tfstats.errors import InvalidSteamIDError, SteamAPIError

def resolve_steamid_or_profile_link(query:str):
    """takes a possible SteamID or a vanity URL, 
    and returns the corresponding SteamID as an int.
    Throws: tfstats.errors.InvalidSteamIDError"""

    # very rough check if query could possibly be a SteamID64
    if len(query) == 17 and query.isdigit():
        # To check if the query is a valid SteamID64
        # we query the steam account level of the given ID,
        # since this is the smallest (and hopefully fastest) API
        # I could find to accomplish this.
        # When asked to resolve an invalid ID, the API either
        # returns a HTTP code 500 or an empty JSON object.
        response = requests.get(steam_api.STEAM_API_PLAYERSUMMARY_URL % (tfstats.settings.STEAM_API_KEY, query))
        if response.status_code == 500:
            raise InvalidSteamIDError()
        if response.status_code != 200:
            raise SteamAPIError(response.status_code)
        try:
            id_str = json.loads(response.text)["response"]["players"][0]["steamid"]
            return int(id_str)
        except KeyError:
            raise InvalidSteamIDError()
        
    # check if query is a valid vanity URL
    response = requests.get(steam_api.STEAM_API_RESOLVEVANITYURL_URL % (tfstats.settings.STEAM_API_KEY, query))
    if response.status_code == 500:
        raise InvalidSteamIDError()
    if response.status_code != 200:
        raise SteamAPIError(response.status_code)
    try:
        decoded_json = json.loads(response.text)["response"]
    except (KeyError, json.decoder.JSONDecodeError):
        raise InvalidSteamIDError()
    if not decoded_json["success"] == 1:
        raise InvalidSteamIDError()
    else:
        return int(decoded_json["steamid"])
