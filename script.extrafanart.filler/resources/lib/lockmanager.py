import os
import xbmcvfs
import xbmc
import xbmcgui
from pathlib import Path
from resources.lib.constants import Addon, Localize
from resources.lib.log_kodi import debug, info, warn, error


LOCK_PATH = Path(xbmcvfs.translatePath(Addon.PROFILE))
LOCK_FILE = str(LOCK_PATH / "lock")

def acquire_lock(show_notification=True):
    os.makedirs(LOCK_PATH, exist_ok=True)
    if xbmcvfs.exists(LOCK_FILE):
        if show_notification:
            xbmcgui.Dialog().notification(Addon.NAME, Localize.OPERATION_RUNNING, xbmcgui.NOTIFICATION_WARNING, 3000)
        return False
    f = xbmcvfs.File(LOCK_FILE, 'w')
    f.write(b"locked\n")
    f.close()
    return True

def release_lock():
    try:
        xbmcvfs.delete(LOCK_FILE)
    except Exception:
        pass

class ShutdownMonitor(xbmc.Monitor):
    def onAbortRequested(self):
        release_lock()

shutdown_monitor = ShutdownMonitor()
