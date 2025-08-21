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















https://chatgpt.com/share/68a5aaa3-d434-800f-9e00-01863535be16


import subprocess
import random
import time
import xml.etree.ElementTree as ET
import re

class CameraTester:
    def __init__(self):
        self.coords = {}
        self.screen = (1080, 2400)  # default; updated at runtime
        self.get_screen_size()

    # ------------------ Shell Helpers ------------------
    def sh(self, cmd, capture=True):
        return subprocess.run(cmd, shell=True, capture_output=capture)

    def adb_tap(self, coord):
        subprocess.run(f"adb shell input tap {coord[0]} {coord[1]}", shell=True)

    def adb_swipe(self, x1, y1, x2, y2, dur=300):
        subprocess.run(f"adb shell input swipe {x1} {y1} {x2} {y2} {dur}", shell=True)

    def get_screen_size(self):
        try:
            out = self.sh("adb shell wm size").stdout.decode(errors="ignore")
            m = re.search(r'Physical size:\s*(\d+)x(\d+)', out)
            if m:
                self.screen = (int(m.group(1)), int(m.group(2)))
        except Exception:
            pass  # keep default

    # ------------------ UI Dump ------------------
    def dump_ui_and_parse(self):
        try:
            self.sh("adb shell uiautomator dump /sdcard/window_dump.xml")
            self.sh("adb pull /sdcard/window_dump.xml .")

            tree = ET.parse("window_dump.xml")
            root = tree.getroot()
            self.coords.clear()

            for node in root.findall(".//node"):
                text = node.attrib.get("text") or ""
                desc = node.attrib.get("content-desc") or ""
                resid = node.attrib.get("resource-id") or ""
                label = text or desc or resid
                bounds = node.attrib.get("bounds")
                if label and bounds:
                    x1, y1, x2, y2 = [
                        int(n) for n in bounds.replace("][", ",").replace("[", "").replace("]", "").split(",")
                    ]
                    self.coords[label] = ((x1 + x2) // 2, (y1 + y2) // 2)
        except Exception as e:
            print("⚠ Error parsing UI dump:", e)

    # ------------------ Label Matching ------------------
    @staticmethod
    def _norm(s: str) -> str:
        return re.sub(r'[^a-z0-9]+', '', (s or '').lower())

    def get_coord(self, *keywords):
        """
        Robust fuzzy match: normalize both label and keywords, allow partials.
        """
        norm_keywords = [self._norm(k) for k in keywords if k]
        for label, coord in self.coords.items():
            nl = self._norm(label)
            for nk in norm_keywords:
                if nk and (nk in nl or nl in nk):  # partial match either way
                    return coord
        return None

    # Try to reveal modes on bottom strip by swiping
    def swipe_mode_strip(self, direction="left", times=1):
        w, h = self.screen
        y = int(h * 0.90)  # bottom strip
        x_left = int(w * 0.25)
        x_right = int(w * 0.75)
        for _ in range(times):
            if direction == "left":
                self.adb_swipe(x_right, y, x_left, y, 250)  # show modes to the right
            else:
                self.adb_swipe(x_left, y, x_right, y, 250)  # show modes to the left
            time.sleep(0.7)

    def ensure_mode_visible(self, keywords, open_more=False, retries=3):
        """
        Find a coord by keywords. If not found:
          - swipe the bottom strip left/right a few times
          - if open_more=True, try to tap "More" and search inside
        Returns coord or None.
        """
        # 1) direct
        coord = self.get_coord(*keywords)
        if coord:
            return coord

        # 2) try swiping strip (both directions)
        for _ in range(retries):
            self.swipe_mode_strip("left", times=1)
            self.dump_ui_and_parse()
            coord = self.get_coord(*keywords)
            if coord:
                return coord

        for _ in range(retries):
            self.swipe_mode_strip("right", times=1)
            self.dump_ui_and_parse()
            coord = self.get_coord(*keywords)
            if coord:
                return coord

        # 3) try opening "More"
        if open_more:
            more_keywords = ["more", "moremodes", "moreoptions", "modes", "mode"]
            more_coord = self.get_coord(*more_keywords)
            if more_coord:
                self.adb_tap(more_coord)
                time.sleep(1.5)
                self.dump_ui_and_parse()
                coord = self.get_coord(*keywords)
                if coord:
                    return coord
                # try small scroll inside More grid (if paginated)
                w, h = self.screen
                self.adb_swipe(int(w*0.8), int(h*0.8), int(w*0.2), int(h*0.8), 250)
                time.sleep(0.7)
                self.dump_ui_and_parse()
                coord = self.get_coord(*keywords)
                if coord:
                    return coord

        return None

    # ------------------ Actions ------------------
    def launch_camera(self):
        print("📷 Launching Camera...")
        self.sh("adb shell am start -n com.oplus.camera/.Camera")
        time.sleep(2.5)

    def capture_photo(self):
        print("📸 Capturing Photo (KEYEVENT)...")
        self.sh("adb shell input keyevent 27")
        time.sleep(1.5)

    def record_video(self):
        try:
            # Launch system video capture intent (most reliable across OEMs)
            video_launch = self.sh("adb shell am start -a android.media.action.VIDEO_CAPTURE")
            if video_launch.returncode == 0:
                print("🎥 Video mode launched")
            else:
                print("❌ Failed to launch video mode")
                return
            time.sleep(2.5)

            # Start recording
            start_video = self.sh("adb shell input keyevent 27")
            if start_video.returncode == 0:
                print("▶️ Video recording started")
            else:
                print("❌ Failed to start recording")
                return

            time.sleep(5)  # record for 5 seconds

            # Stop recording (saves)
            stop_video = self.sh("adb shell input keyevent 27")
            if stop_video.returncode == 0:
                print("⏹ Video recording stopped & saved")
            else:
                print("❌ Failed to stop recording")

            time.sleep(1.2)

            # Return to camera (one back press)
            back_img = self.sh("adb shell input keyevent 4")
            if back_img.returncode == 0:
                print("↩️ Returned to Photo mode")
            else:
                print("❌ Back action failed")
        except Exception as e:
            print("⚠ Error in record_video():", e)

    def cam_flip(self):
        print("🔄 Switching Camera...")
        # Look for typical labels (front/rear/switch icons often have content-desc)
        coord = self.ensure_mode_visible(
            ["switch", "cameraswitch", "flip", "front", "rear", "selfie", "togglecamera"],
            retries=1
        )
        if coord:
            self.adb_tap(coord)
            time.sleep(1.5)
        else:
            print("❌ Switch Camera button not found!")

    def zoom_in(self):
        coord = self.get_coord("zoom", "seekbar", "slider")
        if coord:
            print("🔍 Zoom in...")
            x, y = coord
            # On many Oplus devices, moving LEFT increases zoom (1x -> 2x)
            self.adb_swipe(x, y, x - 200, y, 300)
            time.sleep(1.2)
        else:
            print("⚠ Zoom control not found")

    def zoom_out(self):
        coord = self.get_coord("zoom", "seekbar", "slider")
        if coord:
            print("🔍 Zoom out...")
            x, y = coord
            # Moving RIGHT decreases zoom (2x -> 1x)
            self.adb_swipe(x, y, x + 200, y, 300)
            time.sleep(1.2)
        else:
            print("⚠ Zoom control not found")

    def toggle_flash(self):
        coord = self.get_coord("flash", "torch", "flashlight")
        if coord:
            print("💡 Toggling Flashlight...")
            self.adb_tap(coord)
            time.sleep(1.2)
        else:
            print("⚠ Flashlight button not found")

    # ------------------ New Camera Modes ------------------
    def mode_night(self):
        print("🌙 Switching to Night mode...")
        # robust synonyms
        coord = self.ensure_mode_visible(
            ["night", "nightmode", "ultranight", "nightscene"],
            open_more=False, retries=2
        )
        if coord:
            self.adb_tap(coord)
            time.sleep(1.5)
        else:
            print("⚠ Night mode not found")

    def mode_portrait(self):
        print("👤 Switching to Portrait mode...")
        coord = self.ensure_mode_visible(
            ["portrait", "bokeh", "portraitmode"],
            open_more=False, retries=2
        )
        if coord:
            self.adb_tap(coord)
            time.sleep(1.5)
        else:
            print("⚠ Portrait mode not found")

    def open_more_and_select(self, keywords):
        print(f"📂 Opening More…")
        # Make sure "More" button is visible
        more = self.ensure_mode_visible(
            ["more", "moremodes", "moreoptions", "modes", "mode"],
            open_more=False, retries=3
        )
        if not more:
            print("⚠ More button not found")
            return False

        self.adb_tap(more)
        time.sleep(1.2)
        self.dump_ui_and_parse()

        # Now find the target option inside More
        target = self.get_coord(*keywords)
        if not target:
            # try a small swipe within More list/grid in case it's not on first page
            w, h = self.screen
            self.adb_swipe(int(w*0.85), int(h*0.7), int(w*0.2), int(h*0.7), 250)
            time.sleep(0.7)
            self.dump_ui_and_parse()
            target = self.get_coord(*keywords)

        if target:
            self.adb_tap(target)
            print(f"✅ Selected: {keywords[0]}")
            time.sleep(1.5)
            return True
        else:
            print(f"⚠ Mode not found inside More: {keywords}")
            # go back from More
            self.sh("adb shell input keyevent 4")
            return False

    def mode_slowmotion(self):
        print("🐢 Switching to Slow Motion…")
        self.open_more_and_select(["slomo", "slowmo", "slowmotion", "slo-mo"])

    def mode_timelapse(self):
        print("⏱️ Switching to Time-Lapse…")
        self.open_more_and_select(["timelapse", "time-lapse", "time"])

    def mode_panorama(self):
        print("🧭 Switching to Panorama…")
        self.open_more_and_select(["panorama", "pano"])

    def mode_pro(self):
        print("🛠️ Switching to Pro…")
        self.open_more_and_select(["pro", "expert", "manual"])

    # ------------------ Random Test ------------------
    def random_test(self, duration=60):
        actions = [
            self.capture_photo,
            self.record_video,
            self.cam_flip,
            self.zoom_in,
            self.zoom_out,
            self.toggle_flash,
            self.mode_night,
            self.mode_portrait,
            self.mode_slowmotion,
            self.mode_timelapse,
            self.mode_panorama,
            self.mode_pro
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
