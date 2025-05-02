import os
import shutil
import time
import logging
import subprocess

from cleaner.core import cleanup_options

logging.basicConfig(filename="cleanup_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

user_temp = os.getenv("TEMP") or ""
local_appdata = os.getenv("LOCALAPPDATA") or "C:\\Users\\Default\\AppData\\Local"
appdata = os.getenv("APPDATA") or "C:\\Users\\Default\\AppData\\Roaming"
total_storage_saved = 0

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

    top_line = gradient_line(width, cyan, magenta)
    top_left_color = top_line[0][:3]
    top_right_color = top_line[-1][:3]
    print(color_text(*top_left_color, "╔") + ''.join(color_text(r, g, b, ch) for r, g, b, ch in top_line) + color_text(*top_right_color, "╗"))

    for i, content in enumerate(lines):
        left_color = vertical_gradient(i, len(lines), cyan, magenta)
        right_color = vertical_gradient(i, len(lines), magenta, cyan)
        left = color_text(*left_color, "║")
        right = color_text(*right_color, "║")
        print(f"{left} {content.ljust(width - 2)} {right}")

    bottom_line = gradient_line(width, magenta, cyan)
    bot_left_color = bottom_line[0][:3]
    bot_right_color = bottom_line[-1][:3]
    print(color_text(*bot_left_color, "╚") + ''.join(color_text(r, g, b, ch) for r, g, b, ch in bottom_line) + color_text(*bot_right_color, "╝"))

def emoji_center(text, emoji_left="", emoji_right="", width=54):
    padded = text.center(width - len(emoji_left) - len(emoji_right) - 2)
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
    for key, opt in cleanup_options.items():  # ✅ FIXED: added ()
        label = f"{key}. {opt['label']} [{opt['risk']}]"
        option_lines.append(label)
    option_lines.append("13. Clean All [MIXED]")
    option_lines.append("14. Exit")

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
    total_storage_saved += saved
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

def clean_all():
    for key, opt in cleanup_options.items():  # ✅ FIXED: added ()
        if key == "5":
            reset_store_cache()
            total_storage_saved += 10 * 1024 * 1024
        else:
            clean_folder(opt["path"], opt["label"])
    print("✓ All cleaning tasks completed.")
    logging.info("Performed full cleanup.")
    print_storage_box(total_storage_saved)

def gradient_text(text):
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
    command = (
        'start cmd /k "echo --- Cleanup Log Monitor --- && '
        'powershell -Command \\"Get-Content cleanup_log.txt -Wait\\""'
    )
    os.system(command)

def main():
    global total_storage_saved
    # open_log_window()
    while True:
        print_menu()
        choice = input("Select an option (1-14): ").strip()
        if choice in cleanup_options:
            opt = cleanup_options[choice]
            print(f"\n-- {opt['label']} ({opt['risk']}) --\n{opt['desc']}\n")
            confirm = input("Proceed with cleanup? (y/n): ").lower()
            if confirm == "y":
                if choice == "5":
                    reset_store_cache()
                    total_storage_saved += 10 * 1024 * 1024
                else:
                    clean_folder(opt["path"], opt["label"])
        elif choice == "8":
            confirm = input("Are you sure you want to clean everything? This could damage your Windows installation in some cases! (y/n): ").lower()
            if confirm == "y":
                clean_all()
        elif choice == "9":
            print("Exiting...")
            break
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
