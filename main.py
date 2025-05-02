import os
import shutil
import time
import logging
import subprocess

# Setup logging
logging.basicConfig(filename="cleanup_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

user_temp = os.getenv("TEMP") or ""
local_appdata = os.getenv("LOCALAPPDATA") or "C:\\Users\\Default\\AppData\\Local"
appdata = os.getenv("APPDATA") or "C:\\Users\\Default\\AppData\\Roaming"
total_storage_saved = 0

# Define cleanup targets
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

#def print_menu():
#    print("\n==============================")
#    print("     WINDOWS 11 CLEANER")
#    print("==============================")
#    for key, opt in cleanup_options.items():
#        print(f"{key}. {opt['label']} [{opt['risk']}]")
#    print("8. Clean All [MIXED]")
#    print("9. Exit")
#    print("==============================")

def get_folder_size(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
            except:
                continue
    return total

def human_readable(size_bytes):
    return f"{round(size_bytes / (1024 * 1024), 2)} MB"

def print_storage_box(saved_bytes):
    saved_mb = human_readable(saved_bytes)
    width = 54
    lines = [
        "📦 CLEANUP SUMMARY 📦".center(width - 2),
        f"Total Storage Freed: {saved_mb}".center(width - 2)
    ]
    print_box(lines, width)


def gradient_line(width, start_color, end_color, char="═"):
    result = []
    for i in range(width):
        ratio = i / (width - 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        result.append((r, g, b, char))
    return result

def vertical_gradient(index, total, start_color, end_color):
    ratio = index / (total - 1) if total > 1 else 0
    r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
    g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
    b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
    return r, g, b

def color_text(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def print_box(lines, width=54):
    cyan = (0, 255, 255)
    magenta = (255, 0, 255)

    # Top border: Cyan -> Magenta
    top_line = gradient_line(width, cyan, magenta)
    top_left_color = top_line[0][:3]
    top_right_color = top_line[-1][:3]
    print(color_text(*top_left_color, "╔") + ''.join(color_text(r, g, b, ch) for r, g, b, ch in top_line) + color_text(*top_right_color, "╗"))

    # Side lines with vertical gradients
    for i, content in enumerate(lines):
        # Left side: Cyan → Magenta
        left_color = vertical_gradient(i, len(lines), cyan, magenta)
        # Right side: Magenta → Cyan
        right_color = vertical_gradient(i, len(lines), magenta, cyan)
        left = color_text(*left_color, "║")
        right = color_text(*right_color, "║")
        print(f"{left} {content.ljust(width - 2)} {right}")

    # Bottom border: Magenta -> Cyan
    bottom_line = gradient_line(width, magenta, cyan)
    bot_left_color = bottom_line[0][:3]
    bot_right_color = bottom_line[-1][:3]
    print(color_text(*bot_left_color, "╚") + ''.join(color_text(r, g, b, ch) for r, g, b, ch in bottom_line) + color_text(*bot_right_color, "╝"))

def emoji_center(text, emoji_left="", emoji_right="", width=54):
    clean_text = text
    padded = clean_text.center(width - len(emoji_left) - len(emoji_right) - 2)
    return f"{emoji_left}{padded}{emoji_right}"

def print_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    width = 54

    saved_readable = human_readable(total_storage_saved)
    title_lines = [
        "WINDOWS 11 CLEANER".center(width - 2),
        "by youngjibbit".center(width - 2),
        f"Cleaned: {saved_readable}".center(width - 2)
    ]
    print_box(title_lines, width)

    option_lines = []
    for key in cleanup_options:
        label = f"{key}. {cleanup_options[key]['label']} [{cleanup_options[key]['risk']}]"
        option_lines.append(label)
    option_lines.append("8. Clean All [MIXED]")
    option_lines.append("9. Exit")

    print_box(option_lines, width)

def clean_folder(path, label):
    global total_storage_saved

    if not os.path.exists(path):
        print(f"[!] Path does not exist: {path}")
        return 0
    print(f"Cleaning: {label}")
    before = get_folder_size(path)
    deleted = 0
    failed = 0
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        try:
            if os.path.isfile(full_path) or os.path.islink(full_path):
                os.unlink(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path, ignore_errors=True)
            deleted += 1
        except Exception as e:
            failed += 1
            logging.warning(f"Failed to delete {full_path}: {e}")
    after = get_folder_size(path)
    saved = before - after
    total_storage_saved += saved  # <== Update global value
    print(f"✓ Done. Deleted: {deleted}, Failed: {failed}")
    logging.info(f"{label} - Deleted {deleted}, Failed {failed}, Freed {saved} bytes")
    time.sleep(1)
    return saved

def reset_store_cache():
    global total_storage_saved
    print("Resetting Microsoft Store cache...")
    os.system("start /wait wsreset.exe")
    logging.info("Reset Microsoft Store cache (size freed unknown)")
    print("✓ Done (Store window will close if successful)")
    time.sleep(1)

    # You can assume a small cache size, like 10MB (if desired)
    # estimated_freed = 10 * 1024 * 1024
    # total_storage_saved += estimated_freed


def clean_all():
    for key in cleanup_options:
        if key == "5":
            reset_store_cache()
        else:
            clean_folder(cleanup_options[key]["path"], cleanup_options[key]["label"])
    print("✓ All cleaning tasks completed.")
    logging.info("Performed full cleanup.")
    print_storage_box(total_storage_saved)

def gradient_text(text):
    # Cyan to Magenta vertical gradient for each line (uses RGB ANSI codes)
    cyan = (0, 255, 255)
    magenta = (255, 0, 255)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        ratio = i / max(len(lines) - 1, 1)
        r = int(cyan[0] + (magenta[0] - cyan[0]) * ratio)
        g = int(cyan[1] + (magenta[1] - cyan[1]) * ratio)
        b = int(cyan[2] + (magenta[2] - cyan[2]) * ratio)
        print(f"\033[38;2;{r};{g};{b}m{line}\033[0m")

def open_log_window():
    # Open a new terminal window that live-refreshes the log file
    command = (
        'start cmd /k "echo --- Cleanup Log Monitor --- && '
        'powershell -Command \\"Get-Content cleanup_log.txt -Wait\\""'
    )
    os.system(command)

def main():
    global total_storage_saved  # Needed to modify global variable
    #open_log_window()
    while True:
        print_menu()
        choice = input("Select an option (1-12): ").strip()
        if choice in cleanup_options:
            opt = cleanup_options[choice]
            print(f"\n-- {opt['label']} ({opt['risk']}) --\n{opt['desc']}\n")
            confirm = input("Proceed with cleanup? (y/n): ").lower()
            if confirm == "y":
                if choice == "5":
                    reset_store_cache()
                    # Optional: estimate space cleared
                    # total_storage_saved += 10 * 1024 * 1024
                else:
                    saved = clean_folder(opt["path"], opt["label"])
                    # No need to update total_storage_saved here;
                    # it's already updated inside clean_folder()
        elif choice == "8":
            confirm = input("Are you sure you want to clean everything? this could damage your windows installation in some cases! (y/n): ").lower()
            if confirm == "y":
                clean_all()
        elif choice == "9":
            print("Exiting...")
            break
        else:
            print("Invalid selection. Please try again.")



if __name__ == "__main__":
    main()
