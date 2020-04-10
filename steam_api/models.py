from django.db import models
import tfstats.settings
import tfstats.errors
import requests
import json
import datetime
from . import tracked_fields

STEAM_API_URL = "https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=440&key=%s&format=json&steamid=%s"

# Create your models here.
class PlayerStat(models.Model):
    steamid = models.BigIntegerField()
    timestamp = models.DateTimeField()
    stats_general_json = models.TextField()
    stats_map_json = models.TextField()
    stats_mvm_json = models.TextField()

    def get_by_steamid(self, steamid):
        response = requests.get(STEAM_API_URL % tfstats.settings.STEAM_API_KEY, steamid)
        if response.status_code == 500:
            raise tfstats.errors.InvalidSteamIDError()
        if response.status_code != 200:
            raise Exception() #TODO proper exception

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
            stats_dict.update({stat["name"], stat["value"]})

        # only include tracked_fields
        stats_general_dict = {}
        for field_name in tracked_fields.GENERAL_FIELDS:
            stat = stats_dict[field_name]
            stats_general_dict.update({stat["name"], stat["value"]})
        
        stats_map_dict = {}
        for field_name in tracked_fields.MAP_FIELDS:
            stat = stats_dict[field_name]
            stats_map_dict.update({stat["name"], stat["value"]})
        
        stats_mvm_dict = {}
        for field_name in tracked_fields.MVM_FIELDS:
            stat = stats_dict[field_name]
            stats_mvm_dict.update({stat["name"], stat["value"]})
        
        self.stats_general_json = json.dumps(stats_general_dict)
        self.stats_map_json = json.dumps(stats_map_dict)
        self.stats_mvm_json = json.dumps(stats_mvm_dict)
        self.timestamp = datetime.datetime()
        self.save()
