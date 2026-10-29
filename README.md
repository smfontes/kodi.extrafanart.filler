# script.extrafanart.filler

This Kodi addon fills in additional fanart (“extrafanart”) for **Movies**, **TV Shows**, and **Movie Sets** using the remote fanart scanned by kodi scrapers.  
The addon fills in artwork URLs directly to Kodi’s `fanart1`, `fanart2`, … `fanart<n>` art types.

This addon **does not download images** and **does not use local artwork**.  
All assignments reference **remote URLs** that have already been stored in the available artwork for the fanart art type.

---

## Features

- Fills in extrafanart remote URLs for Kodi’s `fanart1` … `fanart<n>` artwork fields  
- Supports **Movies**, **TV Shows**, and **Movie Sets**  
- Lets you enable or disable scanning for each media type   
- Preserves existing artwork — does not overwrite existing `fanart<i>` entries  
- Fills gaps in the fanart sequence, starting at `fanart1`  
- Provides a manual full‑library scan from the addon’s program menu  
- Adds an optional context menu item to fill extrafanart for a single item  
- **Dry‑run mode** to simulate filling in fanart values without modifying Kodi’s database  
- **Verbose logging** option for detailed information about the scanning process 
- Generates a **run log** showing the fanarts that have been filled in for each media item  
- Tested on **Kodi v21 (Omega)**

![Program menu](script.extrafanart.filler/resources/screenshotrun.png)

---

## Settings Overview

![Settings](script.extrafanart.filler/resources/screenshotsettings.png)

- **Maximum extrafanart images**  
  Number of slots to fill (`fanart1` … `fanart<n>`).  
  Range: **1–99**

- **Scan Movies / TV Shows / Movie Sets**  
  Enable or disable scanning for each media type.

- **Dry run mode**  
  Simulates filling in fanart artwork entries without writing to the Kodi database.

- **Enable verbose logging**  
  Writes details about the scanning process to the Kodi log.

- **Enable context menu**  
  Adds a context menu item to fill in extrafanart for a single Movie, TV Show, or Movie Set.

---

## How It Works

1. The addon reads the available remote artwork URLs from the existing fanart art type.
2. Existing `fanart<i>` entries are inspected to determine the next free slot.  
3. Available fanart URLs are used to sequentially fill in empty `fanart<i>` art types, filling gaps first.
4. If an available URL is already assigned to a `fanart<i>` slot, it is not added again.
5. Filled in fanart slots are recorded in the run log.  

---

## Limitations

- Artwork is **not downloaded**; only URLs are filled in for the `fanart<i>` artwork of a media item.   
- The addon does not run automatically; you must trigger scans manually or via the context menu.

---

## License

This project is licensed under the **GPLv2** license.
