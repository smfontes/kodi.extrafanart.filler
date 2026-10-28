import sqlite3
import xbmcvfs
import xbmcgui
import os
from pathlib import Path
from resources.lib.constants import Addon, Localize
from resources.lib.log_kodi import debug, info, warn, error

DB_PATH = Path(xbmcvfs.translatePath(Addon.PROFILE))
DB_FILE = DB_PATH / "cache.db"
DB = None
CURSOR = None

def init_db():
    global DB, CURSOR
    os.makedirs(DB_PATH, exist_ok=True)
    DB = sqlite3.connect(DB_FILE)
    CURSOR = DB.cursor()
    CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS provider_cache (
            provider TEXT,
            key TEXT,
            json TEXT,
            PRIMARY KEY(provider, key)
        )
    """)
    DB.commit()

def clear_cache():
    global DB, CURSOR
    try:
        DB.close()
    except:
        pass
    DB = None
    CURSOR = None
    try:
        if xbmcvfs.exists(str(DB_FILE)):
            xbmcvfs.delete(str(DB_FILE))
        xbmcgui.Dialog().notification(Addon.NAME, Localize.CACHE_CLEARED, xbmcgui.NOTIFICATION_INFO, 3000)
    except Exception as e:
        xbmcgui.Dialog().notification(Addon.NAME, f"{Localize.ERROR_CLEARING_CACHE}: {e}", xbmcgui.NOTIFICATION_ERROR, 5000)
        return
    init_db()

def get_cached(provider, key):
    CURSOR.execute("SELECT json FROM provider_cache WHERE provider=? AND key=?", (provider, key))
    row = CURSOR.fetchone()
    return row[0] if row else None

def store_cache(provider, key, json_data):
    CURSOR.execute("REPLACE INTO provider_cache (provider, key, json) VALUES (?, ?, ?)",(provider, key, json_data))
    DB.commit()

def provider_cache_empty(provider):
    CURSOR.execute("SELECT COUNT(*) FROM provider_cache WHERE provider=?", (provider,))
    count = CURSOR.fetchone()[0]
    return count == 0
