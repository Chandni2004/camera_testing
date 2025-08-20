import subprocess
import time
import random
import re
import argparse
import os

class CameraAutomation:

    def __init__(self, duration=2):
        self.duration = duration  # in minutes
        self.coords = {}  # store coordinates dynamically

    # ---------------------- UI Dump Parsing ----------------------
    def dump_ui_and_parse(self):
        DEVICE_FILE = "/sdcard/window_dump.xml"
        LOCAL_FILE = "ui.xml"

        # dump xml
        subprocess.run(["adb", "shell", "uiautomator", "dump", DEVICE_FILE], check=True)
        subprocess.run(["adb", "pull", DEVICE_FILE, LOCAL_FILE], check=True)

        with open(LOCAL_FILE, "r", encoding="utf-8") as f:
            xml_data = f.read()

        nodes = re.findall(
            r'text="(.*?)".*?resource-id="(.*?)".*?content-desc="(.*?)".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
            xml_data, re.DOTALL
        )

        coords_map = {}
        for text, resource, desc, x1, y1, x2, y2 in nodes:
            label = text.strip() or desc.strip() or resource.strip()
            if not label:
                continue
            x_center = (int(x1) + int(x2)) // 2
            y_center = (int(y1) + int(y2)) // 2
            coords_map[label.lower()] = (x_center, y_center)

        self.coords = coords_map
        print("✅ UI elements updated:", self.coords.keys())

    # ---------------------- Camera Operations ----------------------
    def launch_camera(self):
        print("📷 Launching Camera...")
        subprocess.run("adb shell am start -a android.media.action.IMAGE_CAPTURE", shell=True)
        time.sleep(3)
        self.dump_ui_and_parse()

    def capture_photo(self):
        coord = self.get_coord("shutter") or self.get_coord("capture")
        if coord:
            print("📸 Capturing Photo...")
            subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)
            time.sleep(2)

    def start_video(self):
        # Ensure video mode first
        video_mode = self.get_coord("video") or self.get_coord("start video")
        if video_mode:
            print("🎬 Switching to Video Mode...")
            subprocess.run(f"adb shell input tap {video_mode[0]} {video_mode[1]}", shell=True)
            time.sleep(2)

        shutter = self.get_coord("shutter")
        if shutter:
            print("🎥 Recording Video...")
            subprocess.run(f"adb shell input tap {shutter[0]} {shutter[1]}", shell=True)
            time.sleep(5)

    def stop_video(self):
        shutter = self.get_coord("shutter")
        if shutter:
            print("⏹️ Stopping Video...")
            subprocess.run(f"adb shell input tap {shutter[0]} {shutter[1]}", shell=True)
            time.sleep(2)

    def cam_flip(self):
        coord = self.get_coord("switch camera") or self.get_coord("flip")
        if coord:
            print("🔄 Switching Camera...")
            subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)
            time.sleep(2)

    def zoom_in(self):
        coord = self.get_coord("zoom in")
        if coord:
            print("🔍 Zoom In...")
            subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)
            time.sleep(1)

    def zoom_out(self):
        coord = self.get_coord("zoom out")
        if coord:
            print("🔍 Zoom Out...")
            subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)
            time.sleep(1)

    def toggle_flash(self):
        coord = self.get_coord("flash")
        if coord:
            print("💡 Toggling Flash...")
            subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)
            time.sleep(1)

    def snapshot_while_recording(self):
        self.start_video()
        coord = self.get_coord("snapshot")   # fallback
        print("📷 Taking Snapshot While Recording...")
        subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)

    # ---------------------- Helpers ----------------------
    def get_coord(self, keyword):
        for label, coord in self.coords.items():
            if keyword in label:
                return coord
        return None

    def run_random(self):
        self.launch_camera()
        actions = [
            self.capture_photo,
            self.start_video,
            self.stop_video,
            self.cam_flip,
            self.zoom_in,
            self.zoom_out,
            self.toggle_flash,
            self.snapshot_while_recording
        ]

        end_time = time.time() + self.duration * 60
        while time.time() < end_time:
            self.dump_ui_and_parse()  # refresh UI each loop
            action = random.choice(actions)
            try:
                action()
            except Exception as e:
                print("⚠️ Error:", e)
            time.sleep(random.uniform(2, 5))

        print("✅ Test Completed!")


if __name__ == "__main__":
    bot = CameraAutomation(duration=1)  # run for 1 min
    bot.run_random()
