import urllib
import xbmcaddon

from resources.lib import api_kodi
from resources.lib.shutdown import ShutdownHandler
from resources.lib.constants import Key, Setting, Label
from resources.lib.log_kodi import debug, info, warn, error

def get_existing_fanart_slots(art_dict):
    existing = {}
    # ==== Go through all the kodi artwork and keep the ones named fanartN
    for key, url in art_dict.items():
        if key.startswith("fanart") and key != "fanart":
            existing[key] = url
    return existing

def next_free_slot(existing_slots):
    # ==== fanart slots do not have to be assigned in order, there can be gaps
    # ==== Get the current list of fanart indices
    indices = []
    for key in existing_slots.keys():
        suffix = key[6:]
        if suffix.isdigit():
            indices.append(int(suffix))
    # ==== If no numeric slots exist, the first valid slot is 1
    if not indices:
        return 1
    max_index = max(indices)
    # ==== Check all numeric slots from 1..max_index
    for idx in range(1, max_index + 1):
        key = f"fanart{idx}"
        url = existing_slots.get(key)
        # Missing OR empty → free slot
        if url is None or url == "":
            return idx
    # ==== No empty or missing slots → append new one
    return max_index + 1

def unwrap_kodi_url(url):
    # ==== normalize url for printing
    if url.startswith("image://"):
        url = url[len("image://"):]
        if url.endswith("/"):
            url = url[:-1]
        return urllib.parse.unquote(url)
    return url

def get_item_art(item):
    # ==== Get the current art for an item so we don't duplicate it
    art = {}
    if item[Key.TYPE] == Key.MOVIE:
        art = api_kodi.get_movie_art(item[Key.ID])
    elif item[Key.TYPE] == Key.TV:
        art = api_kodi.get_tvshow_art(item[Key.ID])
    elif item[Key.TYPE] == Key.SET:
        art = api_kodi.get_movieset_art(item[Key.ID])
    return art

def fill_in_fanart(item, addon_log):
    title = item[Key.TITLE]
    log_label = Label[item[Key.TYPE]].upper()
    addon_log.start_item(log_label, title)
    addon = xbmcaddon.Addon()
    dry_run = addon.getSettingBool(Setting.DRY_RUN)
    max_slots = addon.getSettingInt(Setting.MAX_SLOTS)
    # ==== Get the list of existing fanartX, it may have gaps
    existing = get_existing_fanart_slots(item[Key.ART])
    num_existing = len(existing)
    if num_existing >= max_slots:
        debug(f"'{title}' already has {num_existing} fanart entries — skipping")
        addon_log.end_item(log_label, title, num_existing, 0, 0, 0)
        return 0
    remaining_slots = max_slots - num_existing
    # ==== Get all the available fanarts
    candidates = api_kodi.get_available_fanart(item)         
    if not candidates:
        debug(f"'{title}' no artwork found — skipping")
        addon_log.end_item(log_label, title, num_existing, 0, 0, 0)
        return 0
    # ==== Get all the urls we don't want to add a duplicate of
    existing_urls = list(existing.values())
    fanart = item.get(Key.ART,{}).get('fanart')
    if fanart:
        existing_urls.append(fanart)
    # ==== find the next empty fanart index
    slot = next_free_slot(existing)
    filled_in_count = 0
    duplicate_count = 0
    # ==== look at the possible fanart urls to use to fill in
    for url in candidates:
        ShutdownHandler.raise_exception_on_abort()
        # ==== See if this fanart is already in the existing fanarts
        if url in existing_urls:
            debug(f"'{title}' already has {unwrap_kodi_url(url)}")
            duplicate_count += 1
            continue
        # ==== Found a candidate that does not exist in a slot, fill in the slot with that url
        slot_name = f"fanart{slot}"
        if dry_run:
            # ==== Do not really fill in the slot
            debug(f"[DRY RUN] {title} Would fill in {slot_name}={unwrap_kodi_url(url)}")
        else:
            # ==== Fill the fanart slot with the url
            if item[Key.TYPE] == Key.MOVIE:
                api_kodi.set_movie_art(item[Key.ID], {slot_name: url})
            elif item[Key.TYPE] == Key.TV:
                api_kodi.set_tvshow_art(item[Key.ID], {slot_name: url})
            elif item[Key.TYPE] == Key.SET:
                api_kodi.set_movieset_art(item[Key.ID], {slot_name: url})
            debug(f"{title} filled in {slot_name}={unwrap_kodi_url(url)}")
        addon_log.fanart_filled(slot_name, unwrap_kodi_url(url)) 
        existing[slot_name] = url
        slot = next_free_slot(existing)
        filled_in_count += 1
        if filled_in_count >= remaining_slots:
            # ==== found enough
            break
    addon_log.end_item(log_label, title, num_existing, len(candidates), duplicate_count, filled_in_count)
    return filled_in_count
