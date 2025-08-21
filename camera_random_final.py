import subprocess
import random
import time
import xml.etree.ElementTree as ET

class CameraTester:
    def __init__(self):
        self.coords = {}

    # ------------------ UI Dump ------------------
    def dump_ui_and_parse(self):
        try:
            subprocess.run("adb shell uiautomator dump /sdcard/window_dump.xml", shell=True, capture_output=True)
            subprocess.run("adb pull /sdcard/window_dump.xml .", shell=True, capture_output=True)

            tree = ET.parse("window_dump.xml")
            root = tree.getroot()
            self.coords.clear()

            for node in root.findall(".//node"):
                label = node.attrib.get("content-desc") or node.attrib.get("resource-id") or node.attrib.get("text")
                bounds = node.attrib.get("bounds")
                if label and bounds:
                    x1, y1, x2, y2 = [int(n) for n in bounds.replace("][", ",").replace("[", "").replace("]", "").split(",")]
                    self.coords[label] = ((x1 + x2) // 2, (y1 + y2) // 2)
        except Exception as e:
            print("⚠ Error parsing UI dump:", e)

    # ------------------ Helper ------------------
    def get_coord(self, *keywords):
        for label, coord in self.coords.items():
            for kw in keywords:
                if kw.lower() in label.lower():
                    return coord
        return None

    def adb_tap(self, coord):
        subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)

    # ------------------ Actions ------------------
    def launch_camera(self):
        print("📷 Launching Camera...")
        subprocess.run("adb shell am start -n com.oplus.camera/.Camera", shell=True)
        time.sleep(3)

    def capture_photo(self):
        print("📸 Capturing Photo (KEYEVENT)...")
        subprocess.run("adb shell input keyevent 27", shell=True)
        time.sleep(2)

    def record_video(self):
        try:
            # Step 1: Launch video mode
            video_launch = subprocess.run(
                "adb shell am start -a android.media.action.VIDEO_CAPTURE",
                shell=True, capture_output=True
            )
            if video_launch.returncode == 0:
                print("🎥 Video mode launched")
            else:
                print("❌ Failed to launch video mode")
                return
            time.sleep(3)

            # Step 2: Start recording
            start_video = subprocess.run("adb shell input keyevent 27", shell=True, capture_output=True)
            if start_video.returncode == 0:
                print("▶️ Video recording started")
            else:
                print("❌ Failed to start recording")
                return

            time.sleep(5)  # record for 5 seconds

            # Step 3: Stop recording
            stop_video = subprocess.run("adb shell input keyevent 27", shell=True, capture_output=True)
            if stop_video.returncode == 0:
                print("⏹ Video recording stopped & saved")
            else:
                print("❌ Failed to stop recording")

            time.sleep(2)

            # Step 4: Return to photo mode (only 1 back press)
            back_img = subprocess.run("adb shell input keyevent 4", shell=True, capture_output=True)
            if back_img.returncode == 0:
                print("↩️ Returned to Photo mode")
            else:
                print("❌ Back action failed")

        except Exception as e:
            print("⚠ Error in record_video():", e)


        except Exception as e:
            print("⚠ Error in record_video():", e)

    def cam_flip(self):
        print("🔄 Switching Camera...")
        coord = self.get_coord("switch", "front", "rear", "camera switch", "flip")
        if coord:
            self.adb_tap(coord)
            time.sleep(2)
        else:
            print("❌ Switch Camera button not found!")

    def zoom_in(self):
        coord = self.get_coord("zoom", "seekbar")
        if coord:
            print("🔍 Zoom in...")
            x, y = coord
            subprocess.run(f"adb shell input swipe {x} {y} {x-200} {y} 300", shell=True)  # LEFT = zoom out
            time.sleep(2)
        else:
            print("⚠ Zoom control not found")

    def zoom_out(self):
        coord = self.get_coord("zoom", "seekbar")
        if coord:
            print("🔍 Zoom out...")
            x, y = coord
            subprocess.run(f"adb shell input swipe {x} {y} {x+200} {y} 300", shell=True)  # RIGHT = zoom in
            time.sleep(2)
        else:
            print("⚠ Zoom control not found")

    def toggle_flash(self):
        coord = self.get_coord("flash", "Flash", "torch")
        if coord:
            print("💡 Toggling Flashlight...")
            self.adb_tap(coord)
            time.sleep(2)
        else:
            print("⚠ Flashlight button not found")

    # ------------------ Random Test ------------------
    def random_test(self, duration=60):
        actions = [
            self.capture_photo,
            self.record_video,
            self.cam_flip,
            self.zoom_in,
            self.zoom_out,
            self.toggle_flash
        ]

        self.launch_camera()
        end_time = time.time() + duration

        while time.time() < end_time:
            self.dump_ui_and_parse()
            action = random.choice(actions)
            try:
                action()
            except Exception as e:
                print("⚠ Error running action:", e)
            time.sleep(random.uniform(2, 5))

        print("✅ Test Completed!")


# ------------------ Run ------------------
if __name__ == "__main__":
    tester = CameraTester()
    tester.random_test(duration=60)
