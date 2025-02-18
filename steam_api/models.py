from django.db import models
from django.utils import timezone
import requests
import json
import datetime
import tfstats.settings
import tfstats.errors
from . import tracked_fields
import steam_api

class PlayerManager(models.Manager):
    pass

class Player(models.Model):
    classes = [
        "Scout",
        "Soldier",
        "Pyro",
        "Demoman",
        "Heavy",
        "Engineer",
        "Medic",
        "Sniper",
        "Spy"
    ]

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
    profile_level = models.PositiveIntegerField(blank=True, null=True)

    # Timestamps
    account_created_at = models.DateTimeField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Game stats
    has_public_stats = models.BooleanField()
    stats_general = models.TextField()
    stats_map = models.TextField()
    stats_mvm = models.TextField()

    # Playtimes
    playtime_440_total = models.PositiveIntegerField(blank=True, null=True)
    playtime_440_2weeks = models.PositiveIntegerField(blank=True, null=True)

    # Other values that save processing time later
    main_class = models.CharField(blank=True, max_length=8)

    def get_profile_level(self, steamid):
        response = requests.get(steam_api.STEAM_API_GETSTEAMLEVEL_URL % (tfstats.settings.STEAM_API_KEY, steamid))
        if response.status_code == 500:
            raise tfstats.errors.InvalidSteamIDError()
        if response.status_code != 200:
            raise tfstats.errors.SteamAPIError(response.status_code)
        try:
            decoded_json = json.loads(response.text)
            decoded_json = decoded_json["response"]
            return int(decoded_json["player_level"])
        except (json.decoder.JSONDecodeError):
            raise tfstats.errors.InvalidSteamIDError()
        except(KeyError):
            return 0

    def from_steamid(self, steamid):
        # Step 1/4: General stats
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
            self.account_created_at = timezone.make_aware(datetime.datetime.fromtimestamp(int(decoded_json["timecreated"])), timezone=datetime.timezone.utc)
        else:
            self.account_created_at = None
            self.has_public_stats = False
            self.save()
            return
        
        # Step 2/4: Steam Level
        self.profile_level = self.get_profile_level(steamid)
        
        # Step 3/4: Game stats
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

        self.stats_general = stats_general_dict
        self.stats_map = stats_map_dict
        self.stats_mvm = stats_mvm_dict

        playtimes = {c: stats_general_dict[c+".accum.iPlayTime"] for c in Player.classes}
        self.main_class = max(playtimes, key=playtimes.get)

        # Step 4/4: Playtime
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
                    # rounded to one decimal
                    self.playtime_440_total = round(game["playtime_forever"] / 6) / 10
                    self.playtime_440_2weeks = round(game["playtime_2weeks"] / 6) / 10
        except KeyError:
            self.playtime_440_total = None
            self.playtime_440_2weeks = None
        self.save()
