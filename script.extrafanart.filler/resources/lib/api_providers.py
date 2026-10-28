# The methods to access tmdb and fanart.tv
import urllib.request
import json
import time
import xbmc
import xbmcaddon

from resources.lib import db_cache
from resources.lib.shutdown import ShutdownHandler, ShutdownException
from resources.lib.error_manager import provider_state
from resources.lib.constants import Localize, Setting, Key, Provider
from resources.lib.log_kodi import debug, info, warn, error

FANARTTV_API_ENDPOINT = "https://webservice.fanart.tv/v3.2"
TMDB_API_ENDPOINT = "https://api.themoviedb.org/3"
FANARTTV_AUTH = "movies/latest"
TMDB_AUTH = "authentication"
TMDB_IMAGE_PREFIX = "https://image.tmdb.org/t/p/original"
FANARTTV_SERIES_ENDPOINT = "https://fanart.tv/series"

# Rate limit the calls to the apis. 
RATE_LIMIT = {
    Key.FANARTTV: 0.40,   # no faster then every 400 ms
    Key.TMDB: 0.15,       # no faster than every 150 ms
}
LAST_CALL = {Key.FANARTTV: 0.0, Key.TMDB: 0.0}

class ProviderUnavailableException(Exception):
    def __init__(self, code, reason):
        super().__init__(code, reason)
        self.code = code
        self.reason = reason

def rate_limit(provider):
    # Make sure at least RATE_LIMIT time has elapsed since LAST_CALL for this provider
    addon = xbmcaddon.Addon()
    if not addon.getSettingBool(Setting.RATE_LIMIT):
        # ==== Only perfornm if enabled
        return
    now = time.monotonic()
    last = LAST_CALL.get(provider, 0.0)
    min_interval = RATE_LIMIT.get(provider, 0.0)
    elapsed = now - last
    remaining = min_interval - elapsed
    if remaining > 0:
        xbmc.sleep(int(remaining * 1000))
    LAST_CALL[provider] = time.monotonic()

def make_api_request(provider, url, timeout=10):
    ShutdownHandler.raise_exception_on_abort()
    try:
        if provider == Key.FANARTTV:
            api_key = xbmcaddon.Addon().getSetting(Setting.FANARTTV_API_KEY)
        elif provider == Key.TMDB:
            api_key = xbmcaddon.Addon().getSetting(Setting.TMDB_API_KEY)
        else:
            return {}
        url = f"{url}?api_key={api_key}"
        rate_limit(provider)
        # ==== Make the request and return the response
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # Make sure shutdown was not initiated while the request was in progress
            ShutdownHandler.raise_exception_on_abort()
            return json.loads(response.read().decode("utf-8"))
    except ShutdownException:
        raise
    except Exception as e:
        # ==== the test_connections method should have caught persistent errors
        # ==== use the kodi log to warn for intermittent errors 
        warn(f"Network error for {provider}: {e} URL={url.split('?', 1)[0]}")
        return {}

def test_connection(provider, timeout=10):
    ShutdownHandler.raise_exception_on_abort()
    try:
        # ==== Get the correct endpoint to test for a good connnection
        if provider == Key.FANARTTV:
            api_key = xbmcaddon.Addon().getSetting(Setting.FANARTTV_API_KEY)
            url = f"{FANARTTV_API_ENDPOINT}/{FANARTTV_AUTH}?api_key={api_key}"
        elif provider == Key.TMDB:
            api_key = xbmcaddon.Addon().getSetting(Setting.TMDB_API_KEY)
            url = f"{TMDB_API_ENDPOINT}/{TMDB_AUTH}?api_key={api_key}" 
        # ==== make the request 
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # Make sure shutdown was not initiated while the request was in progress
            ShutdownHandler.raise_exception_on_abort()
            debug(f"test connection to {provider}:{url} returned {response.status}")
            return response.status
    except ShutdownException:
        raise
    except urllib.error.HTTPError as e:
        # Provide specific info about http errors on auth endpoint
        raise ProviderUnavailableException(e.code, e.reason)
    except:
        # Provide generic error if http fails completely
        raise ProviderUnavailableException(500, "")

def test_connections():
    # ==== See if each of the providers is available. Save any connection errors for reporting to the UI
    connection_errors = {Key.FANARTTV: "", Key.TMDB: "" }
    for provider in [Key.FANARTTV, Key.TMDB]:
        try:
            test_connection(provider)             
        except ProviderUnavailableException as e:
            if e.code == 401:
                # ==== Specifically save the auth error, because it will probably be most common
                connection_errors[provider] = Localize.AUTH_ERROR_0.format(provider)
                warn(f"Authorization Error. Reason: {e.reason}.\nLikely cause is invalid {provider} API key in settings.")
            elif not e.code == 500:
                # ==== group other http erros with general message
                connection_errors[provider] = Localize.HTTP_ERROR_0_1_2.format(provider, e.code, e.reason)
                warn(f"Http Error {e.code}. Reason: {e.reason} for {provider}.")
            else:
                # ==== Provide a message for no HTTP errors
                connection_errors[provider] = Localize.NETWORK_ERROR_0.format(provider)
                warn(f"Network Error for {provider}")
    return connection_errors

def get_fanarttv_backgrounds(fanarttv_id, media_type):
    ShutdownHandler.raise_exception_on_abort()
    cache_key = f"{Key.FANARTTV}:{media_type}:{fanarttv_id}"
    cached = db_cache.get_cached(Key.FANARTTV, cache_key)
    if cached:
        debug(f"FANART.TV: found {cache_key} in cache")
        # ==== Found the fanart links for this id in the cache, return them
        return json.loads(cached)
    debug(f"FANART.TV: Cache miss: {cache_key}")
    if provider_state.ftv_net_error:
        debug("fanart.tv in network failed state, not called")
        return []
    # ==== Item not in cache, provider avilable - make the request
    url = f"{FANARTTV_API_ENDPOINT}/{media_type}/{fanarttv_id}"
    data = make_api_request(Key.FANARTTV,url)
    if data == {}:
        return []
    # ==== Got an answer from the api, return the fanart links
    key = "showbackground" if media_type == Key.TV else "moviebackground"
    items = data.get(key, [])
    result = [{"url": x.get("url"), "provider": Key.FANARTTV} for x in items]
    # ==== cache the result so we will not call the api for this id in the future
    db_cache.store_cache(Key.FANARTTV, cache_key, json.dumps(result))
    return result

def get_tmdb_backdrops(tmdb_id, media_type):
    ShutdownHandler.raise_exception_on_abort()
    cache_key = f"{Key.TMDB}:{media_type}:{tmdb_id}"
    cached = db_cache.get_cached("tmdb", cache_key)
    if cached:
        # ==== Found the fanart links for this id in the cache, return them
        debug(f"TMDB: found {cache_key} in cache")
        return json.loads(cached)
    debug(f"TMDB: Cache miss: {cache_key}")
    if provider_state.tmdb_net_error:
        debug("TMDB in network failed state, not called")
        return []
    # ==== Item not in cache, provider avilable - make the request
    url = f"{TMDB_API_ENDPOINT}/{media_type}/{tmdb_id}/images"
    data = make_api_request(Key.TMDB,url)
    if data == {}:
        return []
    # ==== Got an answer from the api, return the fanart links
    backdrops = []
    for b in data.get("backdrops", []):
        file_path = b.get("file_path")
        if not file_path:
            continue
        backdrops.append({"url": TMDB_IMAGE_PREFIX + file_path, "provider": Key.TMDB})
    # ==== cache the result so we will not call the api for this id in the future
    db_cache.store_cache(Key.TMDB, cache_key, json.dumps(backdrops))
    return backdrops

def get_tmdb_movieset_id(tmdb_movie_id):
    ShutdownHandler.raise_exception_on_abort()
    cache_key = f"{Key.TMDB}:{Key.SET}:{tmdb_movie_id}"
    cached = db_cache.get_cached(Key.TMDB, cache_key)
    if cached:
        # ==== Found the movieset_id for this id in the cache, return it
        debug(f"TMDB: found {cache_key} in cache")
        return cached
    debug(f"TMDB: Cache miss: {cache_key}")
    if provider_state.tmdb_net_error:
        debug("TMDB in network failed state, not called")
        return None
    url = f"{TMDB_API_ENDPOINT}/movie/{tmdb_movie_id}"
    data = make_api_request(Key.TMDB, url)
    if data == {}:
        return None
    collection = data.get("belongs_to_collection")
    if not collection:
        return None
    movieset_id = collection.get("id")
    # ==== cache the result so we will not call the api for this id in the future
    db_cache.store_cache(Key.TMDB, cache_key, movieset_id)
    return movieset_id
