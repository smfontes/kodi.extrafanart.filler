import threading
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.shutdown import ShutdownException
from resources.lib.lockmanager import release_lock
from resources.lib.log_addon import AddonLog
from resources.lib.fanart import get_item_art, fill_in_fanart
from resources.lib.constants import Addon, Localize, Setting, Key, Label
from resources.lib.log_kodi import debug, info, warn, error

class WorkerFillSelected(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = False
        self._monitor = xbmc.Monitor()

    def run(self):
        try:
            debug("Fill fanart from context menu selection: starting")
            item = {}
            item[Key.TYPE] = xbmc.getInfoLabel('ListItem.DBTYPE')+"id"
            item[Key.ID] = int(xbmc.getInfoLabel('ListItem.DBID'))
            item[Key.TITLE] = xbmc.getInfoLabel('ListItem.title')
            item[Key.ART] = get_item_art(item)
            addon_log = AddonLog()
            addon_log.start_run(title=item[Key.TITLE])
            filled = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            processed = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            num_filled = fill_in_fanart(item, addon_log)
            prefix = "[DRY RUN]" if xbmcaddon.Addon().getSettingBool(Setting.DRY_RUN) else ""
            final_msg = f"{prefix} {Localize.ARTWORK_FILLED_0.format(num_filled)}: '{item[Key.TITLE]}'"
            xbmcgui.Dialog().notification(Addon.NAME, final_msg, xbmcgui.NOTIFICATION_INFO, 5000)
            info(f"{prefix}Scanned {Label[item[Key.TYPE]]}: '{item[Key.TITLE]}' - filled in {num_filled} extrafanart images")
            processed[item[Key.TYPE]] = 1
            filled[item[Key.TYPE]] = num_filled
            addon_log.end_run(processed, filled)
        except ShutdownException:
            pass
        except Exception:
            import traceback
            tb = traceback.format_exc()
            error(f"Fill fanart from context menu selection: crashed:\n{tb}")
        finally:
            release_lock()
            debug("Fill fanart from context menu selection: lock released")
