import threading
import xbmc
import xbmcgui
import xbmcaddon

from resources.lib.fanart import fill_in_fanart
from resources.lib import api_kodi
from resources.lib.log_addon import AddonLog
from resources.lib.shutdown import ShutdownHandler, ShutdownException
from resources.lib.lockmanager import release_lock
from resources.lib.constants import Addon, Localize, Setting, Key, Label
from resources.lib.log_kodi import debug, info, warn, error

class WorkerFillAll(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = False
        self._monitor = xbmc.Monitor()
    
    def run(self):
        try:
            addon_log = AddonLog()
            addon_log.start_run()
            # ==== Get the addon settings values
            addon = xbmcaddon.Addon()
            scan_movies = addon.getSettingBool(Setting.SCAN_MOVIES)
            scan_tv_shows = addon.getSettingBool(Setting.SCAN_TV_SHOWS)
            scan_sets = addon.getSettingBool(Setting.SCAN_MOVIE_SETS)
            debug("Starting extrafanart scan")
            # ==== Initialize counters
            processed = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            filled = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            total_processed = 0
            # ==== Get all the media items to find fanart for
            items = []
            if scan_movies:
                items.extend(api_kodi.get_movies())
            if scan_tv_shows:
                items.extend(api_kodi.get_tvshows())
            if scan_sets:
                items.extend(api_kodi.get_moviesets())
            total_items = len(items)
            try:
                # ==== Fill in fanart for each media item
                progress = xbmcgui.DialogProgressBG()
                progress.create(Localize.PROCESSING)
                for item in items:
                    ShutdownHandler.raise_exception_on_abort()
                    item[Key.TYPE] = next(k for k in item.keys() if k in {"movieid", "tvshowid", "setid"})
                    item[Key.ID] = item[item[Key.TYPE]]
                    debug(f"Processing {Label[item[Key.TYPE]]}: {item[Key.TITLE]}")
                    total_processed += 1
                    processed[item[Key.TYPE]] += 1
                    # Do the actual work, get the fanart for this item
                    num_filled = fill_in_fanart(item, addon_log)
                    filled[item[Key.TYPE]] += num_filled
                    percent = int((total_processed / total_items) * 100)
                    progress.update(percent, f"{Localize.PROCESSING} {Label[item[Key.TYPE]]}: {item[Key.TITLE]}")
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
            debug("ExtraFanart scan: crashed") 
            tb = traceback.format_exc()
            error(f" crashed:\n{tb}")
        finally:
            release_lock()
            debug("ExtraFanart scan: lock released") 

    def scan_finished(self, addon_log, processed, filled):
        addon_log.end_run(processed, filled)
        prefix = "[DRY RUN]" if xbmcaddon.Addon().getSettingBool(Setting.DRY_RUN) else ""
        info(f"{prefix}Filled in {filled[Key.MOVIE]} fanarts for {processed[Key.MOVIE]} Movies, "
             f"{filled[Key.TV]} fanarts for {processed[Key.TV]} TV Shows, "
             f"and {filled[Key.SET]} fanarts for {processed[Key.SET]} Movie Sets.")
