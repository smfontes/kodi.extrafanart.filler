import sqlite3
import time
import xbmcvfs
import os
from pathlib import Path
from resources.lib.constants import Addon
from resources.lib.log_kodi import debug, info, warn, error

DB_PATH = Path(xbmcvfs.translatePath(Addon.PROFILE))
DB_FILE = DB_PATH / "assigned_art.db"
DB = None
CURSOR = None

def init_db():
    global DB, CURSOR
    os.makedirs(DB_PATH, exist_ok=True)
    DB = sqlite3.connect(DB_FILE)
    CURSOR = DB.cursor()
    CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS assigned_art (
            url TEXT PRIMARY KEY,
            media_type TEXT,
            media_id INTEGER,
            assigned_key TEXT,
            timestamp INTEGER
        )
    """)
    DB.commit()

def is_used(url):
    CURSOR.execute("SELECT url FROM assigned_art WHERE url=?", (url,))
    return CURSOR.fetchone() is not None

def mark_used(url, media_type, media_id, assigned_key):
    CURSOR.execute(
        "INSERT OR IGNORE INTO assigned_art VALUES (?, ?, ?, ?, ?)",
        (url, media_type, media_id, assigned_key, int(time.time()))
    )
    DB.commit()
