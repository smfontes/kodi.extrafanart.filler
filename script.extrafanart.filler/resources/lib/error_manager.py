import xbmcgui
import xbmcaddon
from resources.lib.db_cache import provider_cache_empty
from resources.lib.constants import Addon, Localize, Key, Option
from resources.lib.log_kodi import debug, info, warn, error

class ProviderState:
    def __init__(self):
        self.ftv_net_error = None
        self.tmdb_net_error = None

provider_state = ProviderState()

def check_errors(connection_errors, sets, request_type, addon_log):
    provider_state.ftv_net_error = ftv_net_error = connection_errors[Key.FANARTTV] != ""
    ftv_cache_empty = provider_cache_empty(Key.FANARTTV)
    provider_state.tmdb_net_error = tmdb_net_error = connection_errors[Key.TMDB] != ""
    tmdb_cache_empty = provider_cache_empty(Key.TMDB)
    can_proceed = {Key.MOVIE: True, Key.SET: True, Key.TV: True}
    messages = []
    if ftv_net_error:
        messages.append(connection_errors[Key.FANARTTV])
        if ftv_cache_empty:
            messages.append(Localize.PROVIDER_UNAVAILABLE_0.format(Key.FANARTTV))
        else:
            messages.append(Localize.PROVIDER_NETWORK_UNAVAILABLE_0.format(Key.FANARTTV))
    if tmdb_net_error:
        messages.append(connection_errors[Key.TMDB])
        if tmdb_cache_empty:
            messages.append(Localize.PROVIDER_UNAVAILABLE_0.format(Key.TMDB))
        else:
            messages.append(Localize.PROVIDER_NETWORK_UNAVAILABLE_0.format(Key.TMDB))
    ftv_unavailable = ftv_net_error and ftv_cache_empty
    tmdb_unavailable = tmdb_net_error and tmdb_cache_empty
    if ftv_unavailable and tmdb_unavailable:
        messages.append(Localize.FILLER_STOPPED)
        can_proceed = {Key.MOVIE: False, Key.SET: False, Key.TV: False}
    elif ftv_unavailable or tmdb_unavailable:
        if sets:
            if request_type == Option.SCAN:
                messages.append(Localize.MOVIESETS_NOT_SCANNED)
            else:
                messages.append(Localize.MOVIESET_FILLER_STOPPED)
        can_proceed[Key.SET] = False
    if messages:
        full_message = "\n".join(messages)
        addon_log.message("\n".join("<ERROR>" + m for m in messages) + "\n" )
        xbmcgui.Dialog().ok(Addon.NAME, full_message)       
    return can_proceed