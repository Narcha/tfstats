class InvalidSteamIDError(Exception):
    """The given SteamID is not valid."""

class SteamAPIError(Exception):
    """The Steam API returned a response code other than 200"""
    def __init__(self, code):
        self.code = code
        super().__init__()

class PrivateStatsError(Exception):
    """The requested stats cannot be accessed, they are set to private."""