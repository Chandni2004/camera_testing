import subprocess
import random
import time
import re
from datetime import datetime

crash_count = 0

# ------------------ Get screen size ------------------
def get_screen_size():
    output = subprocess.check_output("adb shell wm size", shell=True, text=True)
    _, size = output.strip().split(":")
    width, height = map(int, size.strip().split("x"))
    return width, height

# ------------------ Parse Crash ------------------
def parse_crash_log(log_text, last_tap):
    summary = {}
    summary["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crash Type
    if "FATAL EXCEPTION" in log_text:
        summary["Type"] = "FATAL EXCEPTION"
    elif "has died" in log_text:
        summary["Type"] = "Process Died"
    elif "ANR in" in log_text:
        summary["Type"] = "ANR"
    elif "signal" in log_text or "native crash" in log_text:
        summary["Type"] = "Native Crash"
    else:
        summary["Type"] = "Unknown Crash"

    # Tap coordinates
    if last_tap:
        summary["Coordinates"] = f"({last_tap[0]}, {last_tap[1]})"

    # Cause (first relevant line)
    match_cause = re.search(r"(E/.+?: .+)", log_text)
    if match_cause:
        summary["Cause"] = match_cause.group(1)
    else:
        summary["Cause"] = "Unknown"

    return summary

# ------------------ Save summary ------------------
def save_crash_summary(summary):
    global crash_count
    crash_count += 1

    with open("crash_summary.txt", "a", encoding="utf-8") as f:
        f.write(f"[{summary['Timestamp']}] Crash at {summary['Coordinates']}\n")
        f.write(f"Type: {summary['Type']}\n")
        f.write(f"Cause: {summary['Cause']}\n\n")

    # Update total crash count at the end
    with open("crash_summary.txt", "a", encoding="utf-8") as f:
        f.write("--------------------------------\n")
        f.write(f"✅ Total Crashes Detected: {crash_count}\n")

# ------------------ Detect crash ------------------
def app_crashed(package_name, last_tap):
    log = subprocess.check_output("adb logcat -d -v brief", shell=True, text=True)

    if any(err in log for err in ["FATAL EXCEPTION", f"{package_name} has died", "ANR in", "native crash", "signal"]):
        summary = parse_crash_log(log, last_tap)
        save_crash_summary(summary)
        return True
    return False

# ------------------ Random Tap ------------------
def random_tap_until_crash(package_name):
    width, height = get_screen_size()

    subprocess.run("adb logcat -c", shell=True)  # clear logs

    while True:
        x = random.randint(100, width - 100)
        y = random.randint(200, height - 200)
        print(f"Tapping at: {x}, {y}")
        subprocess.run(f"adb shell input tap {x} {y}", shell=True)

        time.sleep(1)

        if app_crashed(package_name, (x, y)):
            print("\n⚠️ Crash detected! Summary saved.")
            break

    print("✅ Random tapping stopped after crash.")

# ------------------ Run ------------------
PACKAGE_NAME = "com.example.crashtapapp"
random_tap_until_crash(PACKAGE_NAME)
