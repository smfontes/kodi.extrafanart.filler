import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.log_addon import show_log_window
from resources.lib.constants import Sender, Localize, Addon
from resources.lib.log_kodi import debug, info, warn, error

def notify_service(method):
    debug(f"calling notify all with -- NotifyAll({Sender.SCRIPT_SENDER},{method}) --")
    xbmc.executebuiltin(f"NotifyAll({Sender.SCRIPT_SENDER},{method})")

def main():
    dialog = xbmcgui.Dialog()
    menu_items = [Localize.RUN_SCAN, Localize.VIEW_LAST_LOG, Localize.CONFIGURE, Localize.CLEAR_CACHE]
    choice = dialog.select(Addon.NAME, menu_items)
    debug(f"Menu choice: {choice}")
    if choice == 0:  # Run scan
        notify_service(Sender.SCRIPT_SCAN_OPERATION)
    elif choice == 1:  # View last log
        show_log_window()
    elif choice == 2:  # Settings
        xbmcaddon.Addon().openSettings()
    elif choice == 3:  # Clear cache
        notify_service(Sender.SCRIPT_CLEAR_CACHE_OPERATION)

if __name__ == "__main__":
    main()
