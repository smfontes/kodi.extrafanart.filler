# The kodi json-rpc API is documented at:
# https://kodi.wiki/view/JSON-RPC_API/v12
#
import json
import xbmc
from resources.lib.constants import Key
from resources.lib.log_kodi import debug, info, warn, error

def rpc(payload):
    payload['jsonrpc'] = "2.0"
    payload['id'] = 1
    return json.loads(xbmc.executeJSONRPC(json.dumps(payload)))

def get_movies():
    payload = {"method": "VideoLibrary.GetMovies",
               "params": {"properties": [Key.UNIQUEID, Key.ART, Key.TITLE]}}
    return rpc(payload).get("result", {}).get("movies", [])

def get_tvshows():
    payload = {"method": "VideoLibrary.GetTVShows",
               "params": {"properties": [Key.UNIQUEID, Key.ART, Key.TITLE]}}
    return rpc(payload).get("result", {}).get("tvshows", [])

def get_moviesets():
    payload = {"method": "VideoLibrary.GetMovieSets",
               "params": {"properties": [Key.TITLE, Key.ART]}}
    return rpc(payload).get("result", {}).get("sets", {})

def get_movie_details(movieid):
    payload = {"method": "VideoLibrary.GetMovieDetails",
               "params": {"movieid": movieid, "properties": [Key.UNIQUEID, Key.ART]}}
    return rpc(payload).get("result", {}).get("moviedetails", {})

def get_tvshow_details(tvshowid):
    payload = {"method": "VideoLibrary.GetTVShowDetails", 
               "params": {"tvshowid": tvshowid, "properties": [Key.UNIQUEID, Key.ART]}}
    return rpc(payload).get("result", {}).get("tvshowdetails", {})

def get_movieset_details(setid):
    payload = {"method": "VideoLibrary.GetMovieSetDetails",
               "params": {"setid": setid, "properties": [Key.TITLE, Key.ART]}}
    return rpc(payload).get("result", {}).get("setdetails", {})    

def get_movies_in_set(setid):
    payload = {"method": "VideoLibrary.GetMovies",
               "params": {"filter": {"setid": setid},"properties": [Key.UNIQUEID, Key.TITLE]}}
    return rpc(payload).get("result", {}).get("movies", [])

def set_movie_art(movieid, art_dict):
    payload = {"method": "VideoLibrary.SetMovieDetails",
               "params": {"movieid": movieid, "art": art_dict}}
    rpc(payload)

def set_tvshow_art(tvshowid, art_dict):
    payload = {"method": "VideoLibrary.SetTVShowDetails",
               "params": {"tvshowid": tvshowid, "art": art_dict}}
    rpc(payload)

def set_movieset_art(moviesetid, art_dict):
    payload = {"method": "VideoLibrary.SetMovieSetDetails",
               "params": {"setid": moviesetid, "art": art_dict}}
    rpc(payload)
