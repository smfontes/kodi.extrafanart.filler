import xbmc
import xbmcaddon
import xbmcgui

from resources.lib.log_kodi import debug, info, warn, error
from resources.lib.thread_fill_all import WorkerFillAll
from resources.lib.thread_fill_selected import WorkerFillSelected
from resources.lib.lockmanager import acquire_lock, release_lock
from resources.lib.constants import Sender, Window, Setting

class ExtrafanartService(xbmc.Monitor):
    def __init__(self):
        super().__init__()
        self.worker = None

    def start_scan(self):
        if not acquire_lock(show_notification=True):
            debug("Cannot start scan — lock is active")
            return
        debug("Starting thread to scan media items")
        self.worker = WorkerFillAll()
        self.worker.start()
        # Worker will release lock when finished

    def start_fill(self):
        if not acquire_lock(show_notification=True):
            debug("Cannot fill in fanart — lock is active")
            return
        debug("Starting thread for context menu operation")
        self.worker = WorkerFillSelected()
        self.worker.start()
        # Worker will release lock when finished

    def onNotification(self, sender, method, data):
        if sender == Sender.SCRIPT_SENDER:
            self.start_scan()
        elif sender == Sender.CONTEXT_MENU_SENDER:
            self.start_fill()

    def onAbortRequested(self):
        debug("Shutdown requested — releasing lock")
        release_lock()

    def onSettingsChanged(self):
        enable_context_menu = xbmcaddon.Addon().getSettingBool(Setting.ENABLE_CONTEXTMENU)
        home = xbmcgui.Window(Window.HOME)
        if enable_context_menu:
            debug(f"set {Sender.ENABLE_CONTEXT_MENU_PROPERTY}")
            home.setProperty(Sender.ENABLE_CONTEXT_MENU_PROPERTY, "True")
        else:
            debug(f"unset {Sender.ENABLE_CONTEXT_MENU_PROPERTY}")
            home.clearProperty(Sender.ENABLE_CONTEXT_MENU_PROPERTY)

    def run(self):
        debug("Service started")
        self.onSettingsChanged()
        while not self.abortRequested():
            xbmc.sleep(250)
        debug("Service exiting")

if __name__ == "__main__":
    service = ExtrafanartService()
    service.run()
