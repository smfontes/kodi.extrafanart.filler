import xbmc
import xbmcaddon
ADDON = xbmcaddon.Addon()

class Localize:
    RUN_SCAN = ADDON.getLocalizedString(30200)
    VIEW_LAST_LOG = ADDON.getLocalizedString(30201)
    CONFIGURE = ADDON.getLocalizedString(30202)
    CLEAR_CACHE = ADDON.getLocalizedString(30203)
    FETCHING = ADDON.getLocalizedString(30300)
    PROCESSING = ADDON.getLocalizedString(30301)
    PLEASE_WAIT = ADDON.getLocalizedString(30302)
    ARTWORK_FILLED_0 = ADDON.getLocalizedString(30400)
    CACHE_CLEARED = ADDON.getLocalizedString(30401)
    ERROR_CLEARING_CACHE = ADDON.getLocalizedString(30402)
    OPERATION_RUNNING = ADDON.getLocalizedString(30403)
    AUTH_ERROR_0 = ADDON.getLocalizedString(30901)
    HTTP_ERROR_0_1_2 = ADDON.getLocalizedString(30902)
    NETWORK_ERROR_0 = ADDON.getLocalizedString(30903)
    PROVIDER_UNAVAILABLE_0 = ADDON.getLocalizedString(30904)
    PROVIDER_NETWORK_UNAVAILABLE_0 = ADDON.getLocalizedString(30905)
    FILLER_STOPPED = ADDON.getLocalizedString(30906)
    MOVIESETS_NOT_SCANNED = ADDON.getLocalizedString(30907)
    MOVIESET_FILLER_STOPPED = ADDON.getLocalizedString(30908)
    
class Addon:
    ID = ADDON.getAddonInfo("id")
    NAME = ADDON.getAddonInfo("name")
    PROFILE = ADDON.getAddonInfo("profile")
    PATH = ADDON.getAddonInfo("path")
    
class Provider:
    FANARTTV = "fanart.tv"
    TMDB = "tmdb"

class Key:
    FANARTTV = Provider.FANARTTV
    TMDB = Provider.TMDB
    TVDB = "tvdb"
    MOVIE = "movie"
    TV = "tv"
    SET = "set"
    TYPE = "type"
    ID = "id"
    TITLE = "title"
    UNIQUEID = "uniqueid"
    ART = "art"

Label = {
    Key.MOVIE: xbmc.getLocalizedString(20338),
    Key.TV: xbmc.getLocalizedString(20364),
    Key.SET: xbmc.getLocalizedString(20141),
}

class Option:
    SCAN = "scan"
    CONTEXT_MENU = "context_menu"

class Sender:
    ENABLE_CONTEXT_MENU_PROPERTY = Addon.ID + ".enable_contextmenu"
    CONTEXT_MENU_SENDER = Addon.ID + ".context_menu"
    CONTEXT_MENU_OPERATION = "fill_in_fanart"
    SCRIPT_SENDER = Addon.ID + ".script"
    SCRIPT_SCAN_OPERATION = "start_scan"
    SCRIPT_CLEAR_CACHE_OPERATION = "clear_cache"

class Window:
    HOME = 10000
    LOG_WINDOW_XML = "addonlog_window.xml"

class Setting:
    DRY_RUN = "dry_run"
    FANARTTV_API_KEY = "fanarttv_api_key" 
    TMDB_API_KEY = "tmdb_api_key"
    MAX_SLOTS = "max_slots"
    SCAN_MOVIES = "scan_movies"
    SCAN_TV_SHOWS = "scan_tv_shows"
    SCAN_MOVIE_SETS = "scan_movie_sets"
    ENABLE_LOGGING = "enable_logging"
    ENABLE_CONTEXTMENU = "enable_contextmenu"
    RATE_LIMIT = "rate_limit"
