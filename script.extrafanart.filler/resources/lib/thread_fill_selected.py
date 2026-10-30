import threading
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.shutdown import ShutdownException
from resources.lib.lockmanager import release_lock
from resources.lib.log_addon import AddonLog
from resources.lib.api_kodi import get_movie_art, get_movieset_art, get_tvshow_art
from resources.lib.fanart import fill_in_fanart
from resources.lib.constants import Addon, Localize, Setting, Key, Label
from resources.lib.log_kodi import debug, info, warn, error

class WorkerFillSelected(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = False
        self._monitor = xbmc.Monitor()

    def get_item(self):
        item = {}
        item[Key.TYPE] = xbmc.getInfoLabel('ListItem.DBTYPE')+Key.ID
        item[Key.ID] = int(xbmc.getInfoLabel('ListItem.DBID'))
        item[Key.TITLE] = xbmc.getInfoLabel('ListItem.title')
        # ==== Get the current art for an item so we don't duplicate it
        art = {}
        if item[Key.TYPE] == Key.MOVIE:
            art = get_movie_art(item[Key.ID])
        elif item[Key.TYPE] == Key.TV:
            art = get_tvshow_art(item[Key.ID])
        elif item[Key.TYPE] == Key.SET:
            art = get_movieset_art(item[Key.ID])
        item[Key.ART] = art
        return item

    def run(self):
        try:
            debug("Fill from context menu selection: starting")
            item = self.get_item()
            addon_log = AddonLog()
            addon_log.start_run(title=item[Key.TITLE])
            # ==== Initialize counters
            processed = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            filled = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            # Do the actual work, get the fanart for this item
            num_filled = fill_in_fanart(item, addon_log)
            prefix = "[DRY RUN]" if xbmcaddon.Addon().getSettingBool(Setting.DRY_RUN) else ""
            final_msg = f"{prefix}{Localize.ARTWORK_FILLED_0.format(num_filled)}: '{item[Key.TITLE]}'"
            xbmcgui.Dialog().notification(Addon.NAME, final_msg, xbmcgui.NOTIFICATION_INFO, 5000)
            xbmc.sleep(50)
            info(f"{prefix}Scanned {Label[item[Key.TYPE]]}: '{item[Key.TITLE]}' - filled in {num_filled} extrafanart images")
            processed[item[Key.TYPE]] = 1
            filled[item[Key.TYPE]] = num_filled
            addon_log.end_run(processed, filled)
        except ShutdownException:
            pass
        except Exception:
            import traceback
            error(f"Fill from context menu selection: crashed:\n{traceback.format_exc()}")
        finally:
            release_lock()
            debug("Fill from context menu selection: ended - lock released")
