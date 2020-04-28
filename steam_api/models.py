from django.db import models
from django.utils import timezone
import tfstats.settings
import tfstats.errors
import requests
import json
import datetime
from . import tracked_fields
import steam_api

class PlayerManager(models.Manager):
    pass

class Player(models.Model):
    class Meta:
        managed = True

    objects = PlayerManager()

    # General information
    steamid = models.BigIntegerField(primary_key=True)
    displayname = models.CharField(max_length = 50)
    avatar_url_small = models.URLField()
    avatar_url_medium = models.URLField()
    avatar_url_full = models.URLField()
    profile_url = models.URLField()
    public_profile = models.BooleanField()

    # Timestamps
    account_created_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Game stats
    has_public_stats = models.BooleanField()
    stats_general_json = models.TextField()
    stats_map_json = models.TextField()
    stats_mvm_json = models.TextField()

    # Playtimes
    playtime_440_total = models.PositiveIntegerField(blank=True, null=True)
    playtime_440_2weeks = models.PositiveIntegerField(blank=True, null=True)


    def from_steamid(self, steamid):
        # Step 1/3: General stats
        response = requests.get(steam_api.STEAM_API_PLAYERSUMMARY_URL % (tfstats.settings.STEAM_API_KEY, steamid))
        if response.status_code == 500:
            raise tfstats.errors.InvalidSteamIDError()
        if response.status_code != 200:
            raise tfstats.errors.SteamAPIError(response.status_code)
        try:
            decoded_json = json.loads(response.text)
            decoded_json = decoded_json["response"]["players"][0]
        except (json.decoder.JSONDecodeError, KeyError):
            raise tfstats.errors.InvalidSteamIDError()

        self.steamid = steamid
        self.displayname = decoded_json["personaname"]
        self.avatar_url_small = decoded_json["avatar"]
        self.avatar_url_medium = decoded_json["avatarmedium"]
        self.avatar_url_full = decoded_json["avatarfull"]
        self.profile_url = decoded_json["profileurl"]
        self.public_profile = decoded_json["communityvisibilitystate"] == 3
        if self.public_profile:
            self.account_created_at = datetime.datetime.fromtimestamp(int(decoded_json["timecreated"]))
        else:
            self.account_created_at = None
            self.has_public_stats = False
            self.save()
            return

        # Step 2/3: Game stats
        response = requests.get(steam_api.STEAM_API_GAMESTATS_URL % (tfstats.settings.STEAM_API_KEY, steamid))
        if response.status_code == 500:
            # the player has their stats set to private
            self.has_public_stats = False
            self.save()
            return
        if response.status_code != 200:
            raise tfstats.errors.SteamAPIError(response.status_code)
        
        self.has_public_stats = True
        decoded_json = json.loads(response.text)["playerstats"]
        stats = decoded_json["stats"]
        self.steamid = decoded_json["steamID"]
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

        # Step 3/3: Playtime
        if not self.has_public_stats:
            self.save()
            return
        response = requests.get(steam_api.STEAM_API_PLAYTIMES_URL % (tfstats.settings.STEAM_API_KEY, steamid))
        if response.status_code == 500:
            self.save()
            return
        if response.status_code != 200:
            raise tfstats.errors.SteamAPIError(response.status_code)

        try:
            decoded_json = json.loads(response.text)["response"]["games"]
            for game in decoded_json:
                if game["appid"] == 440:
                    self.playtime_440_total = game["playtime_forever"] / 60
                    self.playtime_440_2weeks = game["playtime_2weeks"] / 60
        except KeyError:
            self.playtime_440_total = None
            self.playtime_440_2weeks = None
        self.save()
