from django.db import models
from django.utils import timezone
import tfstats.settings
import tfstats.errors
import requests
import json
from . import tracked_fields
import steam_api

# Create your models here.
class PlayerStat(models.Model):
    class Meta:
        managed = True

    steamid = models.BigIntegerField(primary_key=True)
    has_public_stats = models.BooleanField()
    timestamp = models.DateTimeField()
    stats_general_json = models.TextField()
    stats_map_json = models.TextField()
    stats_mvm_json = models.TextField()

    def get_by_steamid(self, steamid):
        response = requests.get(steam_api.STEAM_API_GAMESTATS_URL % (tfstats.settings.STEAM_API_KEY, steamid))
        if response.status_code == 500:
            # this could either be due to a server error on valves part,
            # or due to the user setting his game details to private.

            # Quick and dirty check to see if the user has their game stats set to private:
            if requests.get("https://steamcommunity.com/profiles/76561197968575517/stats/TF2/?xml=1", allow_redirects = False).status_code == 302:
                # yup, it's set to private
                self.has_public_stats = False
                raise tfstats.errors.PrivateStatsError()
            raise tfstats.errors.InvalidSteamIDError()
        if response.status_code != 200:
            raise tfstats.errors.SteamAPIError(response.status_code)

        decoded_json = json.loads(response.text)["playerstats"]
        self.steamid = decoded_json["steamID"]
        stats = decoded_json["stats"]
        del decoded_json, response

        # convert stats to a dict for easier indexing
        stats_dict = {}
        for stat in stats:
            # Filter out all achievement trackers
            if stat["name"][:2] == "TF":
                continue
            stats_dict.update({stat["name"]: stat["value"]})

        # only include tracked_fields
        stats_general_dict = {}
        for field_name in tracked_fields.GENERAL_FIELDS:
            try:
                stat = stats_dict[field_name]
            except KeyError:
                stat = 0
            stats_general_dict.update({field_name: stat})
        
        stats_map_dict = {}
        for field_name in tracked_fields.MAP_FIELDS:
            try:
                stat = stats_dict[field_name]
            except KeyError:
                stat = 0
            stats_map_dict.update({field_name: stat})
        
        stats_mvm_dict = {}
        for field_name in tracked_fields.MVM_FIELDS:
            try:
                stat = stats_dict[field_name]
            except KeyError:
                stat = 0
            stats_mvm_dict.update({field_name: stat})
        
        self.stats_general_json = json.dumps(stats_general_dict)
        self.stats_map_json = json.dumps(stats_map_dict)
        self.stats_mvm_json = json.dumps(stats_mvm_dict)
        self.timestamp = timezone.now()
        self.save()

class PlayerProfile(models.Model):
    steamid = models.BigIntegerField(primary_key=True)
    displayname = models.CharField(max_length = 50)
    timestamp = models.DateTimeField()
    avatar_url_medium = models.URLField()
    avatar_url_full = models.URLField()
    profile_url = models.URLField()
    timecreated = models.DateTimeField()

    def get_by_steamid(self, steamid):
        if not validate_steamid(steamid):
            raise tfstats.errors.InvalidSteamIDError()
        response = requests.get(steam_api.STEAM_API_PLAYERSUMMARY_URL % (tfstats.settings.STEAM_API_KEY, steamid))
        if response.status_code == 500:
            raise tfstats.errors.InvalidSteamIDError()
        if response.status_code != 200:
            raise tfstats.errors.SteamAPIError(response.status_code)
        
        decoded_json = json.loads(response.text)["players"]["0"]
        assert decoded_json["steamid"] == str(steamid)

        self.steamid = steamid
        self.displayname = decoded_json["personaname"]
        self.timestamp = timezone.now()
        self.avatar_url_medium = decoded_json["avatarmedium"]
        self.avatar_url_full = decoded_json["avatarfull"]
        self.profile_url = decoded_json["profileurl"]
        self.timecreated = decoded_json["timecreated"]

        self.save()
