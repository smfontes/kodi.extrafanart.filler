import urllib
import xbmcaddon

from resources.lib import api_kodi, api_providers, db_registry
from resources.lib.shutdown import ShutdownHandler
from resources.lib.constants import Key, Setting
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
    # ==== need normalized url for comparing
    if url.startswith("image://"):
        url = url[len("image://"):]
        if url.endswith("/"):
            url = url[:-1]
        return urllib.parse.unquote(url)
    return url

def get_candidates(item_type, tmdb_id, tvdb_id):
    # ==== Call the provider apis to get all the available fanart urls
    candidates = []
    if item_type == Key.MOVIE:
            candidates += api_providers.get_fanarttv_backgrounds(tmdb_id, "movies")
            candidates += api_providers.get_tmdb_backdrops(tmdb_id, "movie")
    elif item_type == Key.TV:
        if tvdb_id:
            candidates += api_providers.get_fanarttv_backgrounds(tvdb_id, Key.TV)
        if tmdb_id:
            candidates += api_providers.get_tmdb_backdrops(tmdb_id, Key.TV)
    elif item_type == Key.SET:
        if tmdb_id:
            candidates += api_providers.get_fanarttv_backgrounds(tmdb_id, "movies")
    return candidates

def get_item_details(item):
    # ==== Get the info that kodi knows about the item. Need artwork and ids
    details = {}
    if item[Key.TYPE] == Key.MOVIE:
        details = api_kodi.get_movie_details(item[Key.ID])
    elif item[Key.TYPE] == Key.TV:
        details = api_kodi.get_tvshow_details(item[Key.ID])
    elif item[Key.TYPE] == Key.SET:
        details = api_kodi.get_movieset_details(item[Key.ID])
        # ==== kodi does not provide a uniqueid for moviesets, so we have to get it from tmdb
        details[Key.UNIQUEID] = {}
        movies_in_set = api_kodi.get_movies_in_set(item[Key.ID])
        if movies_in_set:
            movie_in_set_tmdbid = movies_in_set[0].get(Key.UNIQUEID, {}).get(Key.TMDB)
            if movie_in_set_tmdbid:
                movieset_tmdbid = api_providers.get_tmdb_movieset_id(movie_in_set_tmdbid)
                details[Key.UNIQUEID] = {Key.TMDB: movieset_tmdbid}
    return details

def fill_in_fanart(item, addon_log):
    if not (item[Key.TYPE] == Key.MOVIE or item[Key.TYPE] == Key.TV or item[Key.TYPE] == Key.SET):
        return 0
    filled_in_count = 0
    title = item[Key.TITLE]
    log_label = item[Key.TYPE].upper()
    details = get_item_details(item)
    tmdb_id = details.get(Key.UNIQUEID,{}).get(Key.TMDB)
    tvdb_id = details.get(Key.UNIQUEID,{}).get(Key.TVDB)
    addon_log.start_item(log_label, title, tmdb_id, tvdb_id)
    if details:
        addon = xbmcaddon.Addon()
        dry_run = addon.getSettingBool(Setting.DRY_RUN)
        max_slots = addon.getSettingInt(Setting.MAX_SLOTS)
        art_dict = details.get("art")
        # ==== Get the list of existing fanartX, it may have gaps
        existing = get_existing_fanart_slots(art_dict)
        num_existing = len(existing)
        if num_existing >= max_slots:
            debug(f"'{title}' already has {num_existing} fanart entries — skipping")
            addon_log.end_item(log_label, title, tmdb_id, tvdb_id, num_existing, 0, 0, 0)
            return 0
        remaining_slots = max_slots - num_existing
        # ==== Get all the available fanarts from the providers
        candidates = get_candidates(item[Key.TYPE], tmdb_id, tvdb_id)          
        if not candidates:
            debug(f"'{title}' no artwork found — skipping")
            addon_log.end_item(log_label, title, tmdb_id, tvdb_id, num_existing, 0, 0, 0)
            return 0
        existing_unwrapped = {unwrap_kodi_url(u) for u in existing.values()}
        # ==== find the next empty fanart index
        slot = next_free_slot(existing)
        duplicate_count = 0
        # ==== look at the possible fanart urls to use to fill in
        for art in candidates:
            ShutdownHandler.raise_exception_on_abort()
            # ==== See if this fanart is already in the existing fanarts
            url = art['url']
            if url in existing_unwrapped:
                debug(f"'{title}' already has {url}")
                duplicate_count += 1
                continue
            # ==== Found a candidate that does not exist in a slot, fill in the slot with that url
            slot_name = f"fanart{slot}"
            if dry_run:
                # ==== Do not really fill in the slot
                debug(f"[DRY RUN] {title} Would fill in {slot_name}={url}")
            else:
                # ==== Fill the fanart slot with the url
                if item[Key.TYPE] == Key.MOVIE:
                    api_kodi.set_movie_art(item[Key.ID], {slot_name: url})
                elif item[Key.TYPE] == Key.TV:
                    api_kodi.set_tvshow_art(item[Key.ID], {slot_name: url})
                elif item[Key.TYPE] == Key.SET:
                    api_kodi.set_movieset_art(item[Key.ID], {slot_name: url})
                db_registry.mark_used(url, item[Key.TYPE], item[Key.ID], slot_name)
                debug(f"{title} filled in {slot_name}={url}")
            addon_log.fanart_filled(slot_name, url) 
            existing[slot_name] = url
            slot = next_free_slot(existing)
            filled_in_count += 1
            if filled_in_count >= remaining_slots:
                # ==== found enough
                break
        addon_log.end_item(log_label, title, tmdb_id, tvdb_id, num_existing, len(candidates), duplicate_count, filled_in_count)
    return filled_in_count
