import xbmc
import xbmcaddon
ADDON = xbmcaddon.Addon()

class Localize:
    RUN_SCAN = ADDON.getLocalizedString(30200)
    VIEW_LAST_LOG = ADDON.getLocalizedString(30201)
    CONFIGURE = ADDON.getLocalizedString(30202)
    PROCESSING = ADDON.getLocalizedString(30300)
    PLEASE_WAIT = ADDON.getLocalizedString(30301)
    ARTWORK_FILLED_0 = ADDON.getLocalizedString(30400)
    OPERATION_RUNNING = ADDON.getLocalizedString(30401)
    
class Addon:
    ID = ADDON.getAddonInfo("id")
    NAME = ADDON.getAddonInfo("name")
    PROFILE = ADDON.getAddonInfo("profile")
    PATH = ADDON.getAddonInfo("path")

class Key:
    MOVIE = "movieid"
    TV = "tvshowid"
    SET = "setid"
    TYPE = "type"
    ID = "id"
    TITLE = "title"
    ART = "art"

Label = {
    Key.MOVIE: xbmc.getLocalizedString(20338),
    Key.TV: xbmc.getLocalizedString(20364),
    Key.SET: xbmc.getLocalizedString(20141),
}

class Sender:
    ENABLE_CONTEXT_MENU_PROPERTY = Addon.ID + ".enable_contextmenu"
    CONTEXT_MENU_SENDER = Addon.ID + ".context_menu"
    SCRIPT_SENDER = Addon.ID + ".script"

class Window:
    HOME = 10000
    LOG_WINDOW_XML = "addonlog_window.xml"

class Setting:
    DRY_RUN = "dry_run"
    MAX_SLOTS = "max_slots"
    SCAN_MOVIES = "scan_movies"
    SCAN_TV_SHOWS = "scan_tv_shows"
    SCAN_MOVIE_SETS = "scan_movie_sets"
    ENABLE_LOGGING = "enable_logging"
    ENABLE_CONTEXTMENU = "enable_contextmenu"
