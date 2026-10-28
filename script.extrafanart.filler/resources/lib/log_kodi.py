import xbmc
import xbmcaddon
from resources.lib.constants import Addon, Setting

def _enabled():
    try:
        return xbmcaddon.Addon().getSettingBool(Setting.ENABLE_LOGGING)
    except Exception:
        return False

def debug(msg):
    if _enabled():
        xbmc.log(f"[{Addon.NAME}] {msg}", xbmc.LOGINFO)

def info(msg):
    xbmc.log(f"[{Addon.NAME}] {msg}", xbmc.LOGINFO)

def warn(msg):
    xbmc.log(f"[{Addon.NAME}] WARNING: {msg}", xbmc.LOGWARNING)

def error(msg):
    xbmc.log(f"[{Addon.NAME}] ERROR: {msg}", xbmc.LOGERROR)
