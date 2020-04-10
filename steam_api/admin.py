from django.contrib import admin
from .models import PlayerStat

# Register your models here.
@admin.register(PlayerStat)
class PlayerStatsAdmin(admin.ModelAdmin):
    pass
