import threading
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.shutdown import ShutdownException
from resources.lib.api_providers import test_connections
from resources.lib.lockmanager import release_lock
from resources.lib.log_addon import AddonLog
from resources.lib.error_manager import check_errors
from resources.lib.fanart import fill_in_fanart
from resources.lib import db_cache, db_registry
from resources.lib.constants import Addon, Localize, Setting, Key, Option, Label
from resources.lib.log_kodi import debug, info, warn, error

class WorkerFillSelected(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = False
        self._monitor = xbmc.Monitor()

    def run(self):
        try:
            debug("WorkerFillSelected: starting")
            item = {}
            item[Key.TYPE] = {"tvshow": Key.TV, "movie": Key.MOVIE, "set": Key.SET}[xbmc.getInfoLabel('ListItem.DBTYPE').lower()]
            item[Key.ID] = int(xbmc.getInfoLabel('ListItem.DBID'))
            item[Key.TITLE] = xbmc.getInfoLabel('ListItem.title')
            debug(f"item: {item}")
            db_cache.init_db()
            filled = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            processed = {Key.MOVIE: 0, Key.TV: 0, Key.SET: 0}
            addon_log = AddonLog()
            addon_log.start_run(title=item[Key.TITLE])
            connection_errors = test_connections()
            can_continue = check_errors(connection_errors, item[Key.TYPE] == Key.SET, Option.CONTEXT_MENU, addon_log)
            if can_continue[item[Key.TYPE]]:
                try:
                    progress = xbmcgui.DialogProgressBG()
                    progress.create(Addon.NAME, "")
                    db_registry.init_db()
                    progress.update(0, f"{Localize.PROCESSING} {Label[item[Key.TYPE]]}: {item[Key.TITLE]}")
                    xbmc.sleep(500)
                    num_filled = fill_in_fanart(item, addon_log)
                    processed[item[Key.TYPE]] = 1
                    filled[item[Key.TYPE]] = num_filled
                    addon_log.end_run(processed, filled)
                    progress.update(100, f"{Localize.PROCESSING} {Label[item[Key.TYPE]]}: {item[Key.TITLE]}")
                    xbmc.sleep(500)
                    prefix = "[DRY RUN]" if xbmcaddon.Addon().getSettingBool(Setting.DRY_RUN) else ""
                    final_msg = f"{prefix} {Localize.ARTWORK_FILLED_0.format(num_filled)}: '{item[Key.TITLE]}'"
                    xbmcgui.Dialog().notification(Addon.NAME, final_msg, xbmcgui.NOTIFICATION_INFO, 5000)
                    info(f"Scanned {item[Key.TYPE]}:{item[Key.TITLE]} - filled in {num_filled} extrafanart images")
                finally:
                    progress.close()
            else:
                log_label = f"<ERROR> {item[Key.TYPE].upper()}"
                title = item[Key.TITLE]
                addon_log.start_item(log_label, item[Key.TITLE], None, None)
                addon_log.end_item(log_label, title, None, None, 0, 0, 0, 0)
                addon_log.end_run(processed, filled)
            debug("WorkerFillSelected: finished")
        except ShutdownException:
            pass
        except Exception:
            import traceback
            tb = traceback.format_exc()
            error(f"WorkerFillSelected crashed:\n{tb}")
        finally:
            release_lock()
            debug("WorkerFillSelected: lock released")
