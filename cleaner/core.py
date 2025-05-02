import os
import logging

logging.basicConfig(filename="cleanup_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")
user_temp = os.getenv("TEMP") or ""
local_appdata = os.getenv("LOCALAPPDATA") or "C:\\Users\\Default\\AppData\\Local"
appdata = os.getenv("APPDATA") or "C:\\Users\\Default\\AppData\\Roaming"

cleanup_options = {
    "1": {
        "label": "User Temp Folder",
        "path": user_temp,
        "risk": "SAFE",
        "desc": "Contains temporary files created by applications under your user account.\nThese can include app installers, extracted archives, or session data. Usually safe to delete unless a program is actively using files here."
    },
    "2": {
        "label": "LocalAppData Temp Folder",
        "path": os.path.join(local_appdata, "Temp"),
        "risk": "SAFE",
        "desc": "App-specific temporary files stored in LocalAppData.\nClearing this can free up space without affecting app functionality, although some apps may recreate these files on next launch."
    },
    "3": {
        "label": "Windows Temp Folder",
        "path": "C:\\Windows\\Temp",
        "risk": "RISKY",
        "desc": "System-wide temporary files.\nMay include logs or temp data from services and drivers. While usually safe, deleting active system-related files may cause errors."
    },
    "4": {
        "label": "Windows Update Cache",
        "path": "C:\\Windows\\SoftwareDistribution\\Download",
        "risk": "RISKY",
        "desc": "Holds Windows update installer files.\nDeleting this will not harm the system but will require re-downloading updates if needed. Avoid if updates are pending or in progress."
    },
    "5": {
        "label": "Microsoft Store Cache",
        "path": "",  # Uses wsreset
        "risk": "SAFE",
        "desc": "Resets and clears cached content for the Microsoft Store.\nFixes Store errors and frees some disk space. Does not affect installed apps."
    },
    "6": {
        "label": "Prefetch Folder",
        "path": "C:\\Windows\\Prefetch",
        "risk": "MODERATE",
        "desc": "Used to accelerate application launch times by caching data.\nCan be deleted to reclaim space or reset app behavior, but Windows will slowly rebuild it, potentially causing slightly slower app launches initially."
    },
    "7": {
        "label": "Recent Files History",
        "path": os.path.join(appdata, "Microsoft\\Windows\\Recent"),
        "risk": "SAFE",
        "desc": "Stores shortcuts to recently accessed files for quick access.\nDeleting does not remove the actual files, only their shortcut history."
    },
    "8": {
        "label": "Windows Error Reports",
        "path": "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportQueue",
        "risk": "SAFE",
        "desc": "Queued error and crash reports for sending to Microsoft.\nThese logs can be deleted without issue, especially if you don't use feedback reporting."
    },
    "9": {
        "label": "Delivery Optimization Files",
        "path": "C:\\Windows\\DeliveryOptimization",
        "risk": "RISKY",
        "desc": "Files used to distribute Windows updates via peer-to-peer.\nDeleting them can free up space, but might interfere with update sharing or require redownloading updates."
    },
    "10": {
        "label": "Thumbnail Cache",
        "path": os.path.join(local_appdata, "Microsoft\\Windows\\Explorer"),
        "risk": "SAFE",
        "desc": "Stores cached thumbnail images for Explorer previews.\nDeleting these may cause temporary lag when opening folders with many images/videos, as thumbnails are regenerated."
    },
    "11": {
        "label": "Windows Logs",
        "path": "C:\\Windows\\Logs",
        "risk": "MODERATE",
        "desc": "Contains logs for system events, services, and diagnostics.\nSafe to delete if not troubleshooting issues, but might erase useful diagnostics data."
    },
    "12": {
        "label": "Software Distribution Metadata",
        "path": "C:\\Windows\\SoftwareDistribution\\DataStore",
        "risk": "MODERATE",
        "desc": "Database storing update history and metadata.\nUseful for diagnosing update issues, but safe to delete if you want to reset Windows Update history."
    }
}