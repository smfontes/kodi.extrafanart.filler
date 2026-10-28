import xbmcaddon
import xbmcvfs
import xbmcgui
import xbmc
import time
import os
from pathlib import Path
from resources.lib.constants import Addon, Localize, Window, Setting, Key
from resources.lib.log_kodi import debug, info, warn, error

LOG_PATH = Path(xbmcvfs.translatePath(Addon.PROFILE))
LOG_FILE = LOG_PATH / "last_run.log"                             

class AddonLog:
    def __init__(self):
        self.prefix = ""

    def start_run(self,title=None):
        addon = xbmcaddon.Addon()
        dry_run = addon.getSettingBool(Setting.DRY_RUN)
        max_slots = addon.getSettingInt(Setting.MAX_SLOTS)
        scan_movies = addon.getSettingBool(Setting.SCAN_MOVIES)
        scan_tv_shows = addon.getSettingBool(Setting.SCAN_TV_SHOWS)
        scan_movie_sets = addon.getSettingBool(Setting.SCAN_MOVIE_SETS)
        self.prefix = "[DRY RUN]" if dry_run else ""
        os.makedirs(LOG_PATH, exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(self.prefix+f"{Addon.NAME}\n")
            f.write(self.prefix+f"Log @ {LOG_FILE}\n")
            if (title):
                 f.write(self.prefix+f"Fill in extrafanart for '{title}'\n")
            else:    
                f.write(self.prefix+f"Enabled: Movies={scan_movies}, Sets={scan_movie_sets}, TV Shows={scan_tv_shows}\n")
            f.write(self.prefix+f"========== Max images to fill in per media item: {max_slots} ==============\n")
            f.write(self.prefix+f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def start_item(self, log_label, title, tmdb_id, tvdb_id):
        text = f" ┌[{log_label}] {title} | TMDB={tmdb_id} TVDB={tvdb_id}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
            
    def fanart_filled(self, slot_name, url):
        text = f" │     {slot_name} = {url}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def end_item(self, log_label, title, tmdb_id, tvdb_id, num_existing, found, duplicate, filled_in):
        text = f" └[{log_label}] {title} | existing={num_existing} | found={found} | duplicate={duplicate} | filled={filled_in}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def message(self, text):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def end_run(self, processed, filled_in):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(self.prefix+"Summary\n")
            f.write(self.prefix+"-------\n")
            f.write(self.prefix+f"Movies processed: {processed[Key.MOVIE]}\n")
            f.write(self.prefix+f"TV shows processed: {processed[Key.TV]}\n")
            f.write(self.prefix+f"Movie Sets processed: {processed[Key.SET]}\n")
            f.write(self.prefix+f"Total media items processed: {processed[Key.MOVIE]+processed[Key.TV]+processed[Key.SET]}\n")
            f.write(self.prefix+f"Movie Fanarts filled: {filled_in[Key.MOVIE]}\n")
            f.write(self.prefix+f"TV Show Fanarts filled: {filled_in[Key.TV]}\n")
            f.write(self.prefix+f"Movie Set Fanarts filled: {filled_in[Key.SET]}\n")
            f.write(self.prefix+f"Total fanarts filled: {filled_in[Key.MOVIE]+filled_in[Key.TV]+filled_in[Key.SET]}\n")
            f.write(self.prefix+f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

class AddonLogWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def onInit(self):
        self.winid = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.getControl(1).setText(Localize.PLEASE_WAIT)
        xbmc.sleep(50)
        text = self.load_log()
        self.getControl(1).setText(text)

    def load_log(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = "No log available."
        return text

def show_log_window():
    win = AddonLogWindow(Window.LOG_WINDOW_XML, Addon.PATH, "default", "720p")
    win.doModal()
    del win
