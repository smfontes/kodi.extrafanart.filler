import threading
import xbmc
import xbmcgui
import xbmcaddon

from resources.lib import api_kodi, api_providers, db_cache, db_registry
from resources.lib.fanart import fill_in_fanart
from resources.lib.log_addon import AddonLog
from resources.lib.shutdown import ShutdownHandler, ShutdownException
from resources.lib.error_manager import check_errors
from resources.lib.lockmanager import release_lock
from resources.lib.constants import Addon, Localize, Setting, Key, Label
from resources.lib.log_kodi import debug, info, warn, error

class WorkerFillAll(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = False
        self._monitor = xbmc.Monitor()

    def get_items(self, scan_movies, scan_tv_shows, scan_movie_sets):
        items = []
        progress = xbmcgui.DialogProgressBG()
        try:
            progress.create(Addon.NAME)
            if scan_movies:
                # ==== Get all the movies from kodi
                movies = api_kodi.get_movies()
                total = len(movies)
                fetched = 0
                for m in movies:
                    ShutdownHandler.raise_exception_on_abort()
                    title = m.get("title")
                    # ==== Create a standard item for the Movie
                    items.append({Key.TYPE: Key.MOVIE, Key.ID: m['movieid'], Key.TITLE: title})
                    fetched += 1
                    percent = int((fetched / total) * 100)
                    progress.update(percent, f"{Localize.FETCHING} {Label[Key.MOVIE]}:" , title)
                    xbmc.sleep(10)
            if scan_tv_shows:
                # ==== Get all the TV Shows from kodi
                tvshows = api_kodi.get_tvshows()
                total = len(tvshows)
                fetched = 0
                for s in tvshows:
                    ShutdownHandler.raise_exception_on_abort()
                    title = s.get("title")
                    # ==== Create a standard item for the TV Show
                    items.append({Key.TYPE: Key.TV, Key.ID: s['tvshowid'], Key.TITLE: title})
                    fetched += 1
                    percent = int((fetched / total) * 100)
                    progress.update(percent, f"{Localize.FETCHING} {Label[Key.TV]}:", title)
                    xbmc.sleep(10)
            if scan_movie_sets:
                # ==== Get all the Movie Sets from kodi
                movie_sets = api_kodi.get_moviesets()
                total = len(movie_sets)
                fetched = 0
                for ms in movie_sets:
                    ShutdownHandler.raise_exception_on_abort()
                    title = ms.get("title")
                    # ==== Create a standard item for the Movie Set
                    items.append({Key.TYPE: Key.SET, Key.ID: ms['setid'], Key.TITLE: title})
                    fetched += 1
                    percent = int((fetched / total) * 100)
                    progress.update(percent, f"{Localize.FETCHING} {Label[Key.SET]}:", title)
                    xbmc.sleep(10)
        finally:
            progress.close()
        return items
    
    def run(self):
        try:
            # ==== Get the addon settings values
            addon = xbmcaddon.Addon()
            scan_movies = addon.getSettingBool(Setting.SCAN_MOVIES)
            scan_tv_shows = addon.getSettingBool(Setting.SCAN_TV_SHOWS)
            scan_sets = addon.getSettingBool(Setting.SCAN_MOVIE_SETS)
            # ==== Initialize the cache and registry databases and the log
            db_registry.init_db()
            db_cache.init_db()
            addon_log = AddonLog()
            addon_log.start_run()
            debug("Starting extrafanart scan")
            # ==== Initialize counters
            filled = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            processed = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            total_processed = 0
            # ==== Test the fanart providers
            connection_errors = api_providers.test_connections()
            # ==== Use the test results to see if we should keep going
            can_continue = check_errors(connection_errors, scan_sets, "scan", addon_log)
            if not ((scan_movies and can_continue[Key.MOVIE]) or 
                    (scan_tv_shows and can_continue[Key.TV]) or 
                    (scan_sets and can_continue[Key.SET])):
                # ==== Nothing can be scanned 
                self.scan_finished(addon_log, processed, filled)
                return
            # ==== Get all the media items to find fanart for
            items = self.get_items(scan_movies and can_continue[Key.MOVIE], 
                                   scan_tv_shows and can_continue[Key.TV], 
                                   scan_sets and can_continue[Key.SET])
            total_items = len(items)
            try:
                # ==== Fill in fanart for each media item
                progress = xbmcgui.DialogProgressBG()
                progress.create(Localize.PROCESSING)
                for item in items:
                    ShutdownHandler.raise_exception_on_abort()
                    title = item[Key.TITLE]
                    debug(f"Processing {item[Key.TYPE]}: {title}")
                    total_processed += 1
                    processed[item[Key.TYPE]] += 1
                    # Do the actual work, get the fanart for this item
                    num_filled = fill_in_fanart(item, addon_log)
                    filled[item[Key.TYPE]] += num_filled
                    percent = int((total_processed / total_items) * 100)
                    progress.update(percent, f"{Localize.PROCESSING} {Label[item[Key.TYPE]]}:", title)
            finally:
                # ==== Finished all of the media items
                progress.close()
                final_msg = Localize.ARTWORK_FILLED_0.format(filled[Key.MOVIE]+filled[Key.TV]+filled[Key.SET])
                xbmcgui.Dialog().notification(Addon.NAME, final_msg, xbmcgui.NOTIFICATION_INFO, 5000)
                self.scan_finished(addon_log, processed, filled) 
                debug("Extrafanart scan completed")
        except ShutdownException:
            pass
        except Exception:
            import traceback
            tb = traceback.format_exc()
            error(f"WorkerFillAll crashed:\n{tb}")
        finally:
            release_lock()
            debug("WorkerFillAll: lock released") 

    def scan_finished(self, runlogger, processed, filled):
        runlogger.end_run(processed, filled)
        info(f"Scanned {processed[Key.MOVIE]} Movies, {processed[Key.TV]} TV Shows, and {processed[Key.SET]} Movie Sets.")
        info(f"Filled in {filled[Key.MOVIE]} fanarts for Movies, {filled[Key.TV]} fanarts for TV Shows, and {filled[Key.SET]} fanarts for Movie Sets.")
