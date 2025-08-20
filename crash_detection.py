import subprocess
import random
import time

# Get screen size automatically
def get_screen_size():
    output = subprocess.check_output("adb shell wm size", shell=True, text=True)
    _, size = output.strip().split(":")
    width, height = map(int, size.strip().split("x"))
    return width, height

# Function to check if app crashed
def app_crashed(package_name):
    log = subprocess.check_output("adb logcat -d -v brief", shell=True, text=True)
    if "FATAL EXCEPTION" in log or f"{package_name} has died" in log:
        return True
    return False

def random_tap_until_crash(package_name):
    width, height = get_screen_size()

    # Clear old logs
    subprocess.run("adb logcat -c", shell=True)

    while True:
        # Random tap
        x = random.randint(100, width - 100)
        y = random.randint(200, height - 200)
        print(f"Tapping at: {x}, {y}")
        subprocess.run(f"adb shell input tap {x} {y}", shell=True)

        # Small delay
        time.sleep(1)

        # Check logs for crash
        if app_crashed(package_name):
            print("\n⚠️ App Crash Detected!")
            break

    print("✅ Random tapping stopped after crash.")

# Run
PACKAGE_NAME = "com.example.crashtapapp"  # replace with your app
random_tap_until_crash(PACKAGE_NAME)
carsh_detect
