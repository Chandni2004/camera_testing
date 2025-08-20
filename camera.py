import subprocess
import re
import time
import argparse
import json
import xml.etree.ElementTree as ET

class camera:
    def devices(self):
        try:
            result = subprocess.run("adb devices", shell=True, capture_output=True)
            if result.returncode == 0:
                device = re.findall(r"\bdevice\b", result.stdout.decode())
                print(device)
                if device:
                    result_camera_on = subprocess.run("adb shell am start -n com.oplus.camera/.Camera", shell=True, capture_output=True)
                    print(result_camera_on.stdout)
                else:
                    print("Failed to find device")
        except Exception as e:
            print("Error in devices():", e)
        time.sleep(5)

    def cam_capture(self):
        try:
            click_img = subprocess.run("adb shell input keyevent 27", shell=True, capture_output=True)
            if click_img.returncode == 0:
                print("Image Captured")
            else:
                print("Failed")
        except Exception as e:
            print("Error in cam_capture():", e)

    def image_back(self):
        try:
            back_img = subprocess.run("adb shell input keyevent 4", shell=True, capture_output=True)
            if back_img.returncode == 0:
                print("Image Captured after move back")
            else:
                print("Failed")
        except Exception as e:
            print("Error in image_back():", e)
        time.sleep(5)

    def open_video(self):
        try:
            video_launch = subprocess.run("adb shell am start -a android.media.action.VIDEO_CAPTURE", shell=True, capture_output=True)
            if video_launch.returncode == 0:
                print("Video launched")
            else:
                print("Failed to launch")
        except Exception as e:
            print("Error in open_video():", e)
        time.sleep(5)

    def video_capture(self):
        try:
            click_video = subprocess.run("adb shell input keyevent 27", shell=True, capture_output=True)
            if click_video.returncode == 0:
                print("Video streaming")
            else:
                print("Failed")
        except Exception as e:
            print("Error in video_capture():", e)
        time.sleep(5)

    def video_back(self):
        try:
            for i in range(4):
                back_img = subprocess.run("adb shell input keyevent 4", shell=True, capture_output=True)
                if back_img.returncode == 0:
                    print("video Captured after move back")
                else:
                    print("Failed")
            time.sleep(5)
        except Exception as e:
            print("Error in video_back():", e)
        time.sleep(5)

    def dumpsys_cam(self):
        try:
            check_camera_devices = subprocess.run("adb shell dumpsys media.camera", shell=True, capture_output=True)
            if check_camera_devices.returncode == 0:
                print(f"Check Camera Devices: {check_camera_devices.stdout.decode()}")
            else:
                print("Failed")
        except Exception as e:
            print("Error in dumpsys_cam():", e)
        time.sleep(2)

    def logcat_cam(self):
        try:
            logcat = subprocess.run("adb logcat -d | grep -i camera > log.txt", shell=True, capture_output=True)
            if logcat.returncode == 0:
                # logs = logcat.stdout.decode()
                print("Filtered logcat output")
                # for line in logs.splitlines():
                #     if "camera" in line.lower():
                #         print(line)
            else:
                print("Failed to get logcat output")
        except Exception as e:
            print("Error in logcat_cam():", e)
        time.sleep(2)


    def log_one(self):
        try:
            log_file = "cap.txt"  # Path to your log file
            search_key = input("Enter the key to search: ")
            with open(log_file, "r") as f:
                content = f.read()
            # print(content)
            # matches = re.findall(rf"{re.escape(search_key)}\s*[:=]\s*(\S+)", content, flags=re.IGNORECASE)
            matches = re.findall(rf"{re.escape(search_key)}\s*[:=]\s*\S+", content, flags=re.IGNORECASE)
            if matches:
                result = {search_key: matches}
            else:
                result = {search_key: None}
            print(result)
        except Exception as e:
            print("Error in log_summary():", e)


    def log_summary(self):
        try:
            log_file = "cap.txt"  # Path to your log file
            summary_file="log_summary.txt"
            search=['resolution','mDate','frameNumber','orientation','mSnapshotmode','burst_shot','timeconsuming','reference','mTimeStamp','mIdentity','sceneMode','mbBurstShot','quick_jpeg','capture_mode','livephoto_enable','success','capture','mId','mcapturetime','fps','zslFrameCount']
            with open(log_file, "r") as f:
                content = f.read()

            summary_data = []
            for key in search:
                match = re.search(rf"{re.escape(key)}\s*[:=]\s*\S+", content, flags=re.IGNORECASE)
                if match:
                    summary_data.append(match.group())
                else:
                    summary_data.append(f"{key}: Not found")

            with open(summary_file,'w') as out:
                for lines in summary_data:
                    out.write(lines+"\n")
                    print(lines)
            print("log summary saved to log_summary")
        except Exception as e:
            print("Error in log_summary():", e)


    def cam_nodes(self):
        try:
            access_nodes = subprocess.run("adb shell ls -l /dev/video*", shell=True, capture_output=True)
            if access_nodes.returncode == 0:
                print(f"Access camera device nodes: {access_nodes.stdout.decode()}")
            else:
                print("Failed")
        except Exception as e:
            print("Error in cam_nodes():", e)


    def cam_flip(self,coordinate):
        # x=input("Enter the x coordinates: ")
        # y=input("Enter the y coordinates: ")

        try:
            with open("camera_json.json","r") as file:
                data=json.load(file)

            # flip_x,flip_y = data["flip_cam"]
            flip_x,flip_y = data[coordinate]
            parser = argparse.ArgumentParser(description="Automate ADB tap for switching camera")
            parser.add_argument('flip_x', type=int, help='X coordinate of the camera switch button')
            parser.add_argument('flip_y', type=int, help='Y coordinate of the camera switch button')
            args = parser.parse_args([str(flip_x),str(flip_y)])
            adb_command = f'adb shell input tap {args.flip_x} {args.flip_y}'
            print(f"Running: {adb_command}")
            subprocess.run(adb_command,shell=True)
        except Exception as e:
            print("Error in cam_flip():", e)

    def snapshot_while_recording(self):
        try:
            # x = int(input("Enter the X coordinate for snapshot: "))
            # y = int(input("Enter the Y coordinate for snapshot: "))
            capture_cmd = f"adb shell input tap {225} {2017}"
            result = subprocess.run(capture_cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                print("Snapshot taken successfully while recording.")
            else:
                print("Failed to take snapshot during recording.")
        except Exception as e:
            print("Error in snapshot_while_recording():", e)

    def file_format(self):
        try:
            cmd = """adb shell "ls -t /sdcard/DCIM/Camera | grep -E '\\.jpg|\\.png|\\.mp4' | head -n 1" """

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                latest_file = result.stdout.strip()
                if latest_file:
                    full_path = f"/sdcard/DCIM/Camera/{latest_file}"
                    print("Latest media file path:", full_path)
                    return full_path
                else:
                    print("No media files found in /sdcard/DCIM/Camera")
            else:
                print("ADB command failed:", result.stderr)

        except Exception as e:
            print("Error:", e)

    def adb_command(self,cmd):

        """Run an ADB command and return its output as text."""
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()

    # def uiautomator(self):
    #     LOCAL_FILE = r"C:\Users\Chandni Shaik\android_testing\ui.xml"
    #     DEVICE_FILE = "/sdcard/ui.xml"
    #     print("📱 Dumping UI hierarchy from device...")
    #
    # # Step 1: Dump and Pull
    #     self.adb_command(["adb", "shell", "uiautomator", "dump", DEVICE_FILE])
    #     self.adb_command(["adb", "pull", DEVICE_FILE, LOCAL_FILE])
    #
    # # Step 2: Parse XML
    #     tree = ET.parse(LOCAL_FILE)
    #     root = tree.getroot()
    #
    #     seen = set()
    #     print("\n=== ADB Tap Commands for Elements ===")
    #     for node in root.iter("node"):
    #         bounds = node.attrib.get("bounds")
    #         text = node.attrib.get("text", "").strip()
    #         desc = node.attrib.get("content-desc", "").strip()
    #         res_id = node.attrib.get("resource-id", "").strip()
    #
    #         if bounds:
    #             coords = [int(x) for x in bounds.replace('][', ',')
    #                             .replace('[', '')
    #                             .replace(']', '')
    #                             .split(',')]
    #             x_center = (coords[0] + coords[2]) // 2
    #             y_center = (coords[1] + coords[3]) // 2
    #             label = text or desc or res_id
    #             if not label:
    #                 continue
    #             if (x_center, y_center) not in seen:
    #                 seen.add((x_center, y_center))
    #                 print(f"{label:30} => adb shell input tap {x_center} {y_center}")
    # def uiautomator(self):
    #     print("Dumping UI hierarchy from device...")
    #
    # # 1. Dump XML on device
    #     result = subprocess.run(
    #         ["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
    #         capture_output=True, text=True
    #     )
    #     print(result.stdout)
    #
    # # 2. Pull file to local
    #     LOCAL_XML = r"C:\Users\Chandni Shaik\android_testing\ui.xml"
    #     LOCAL_TXT = r"C:\Users\Chandni Shaik\android_testing\ui.txt"
    #
    #     subprocess.run(["adb", "pull", "/sdcard/ui.xml", LOCAL_XML], check=True)
    #
    # # 3. Parse XML and convert to TXT
    #     try:
    #         tree = ET.parse(LOCAL_XML)
    #         root = tree.getroot()
    #
    #         seen = set()  # ✅ fix: define seen set
    #
    #         with open(LOCAL_TXT, "w", encoding="utf-8") as f:
    #             for node in root.iter("node"):
    #                 text = node.attrib.get("text", "")
    #                 resource = node.attrib.get("resource-id", "")
    #                 desc = node.attrib.get("content-desc", "")  # ✅ fix: extract desc
    #                 bounds = node.attrib.get("bounds", "")
    #
    #                 f.write(f"Text: {text}, Resource: {resource}, Desc: {desc}, Bounds: {bounds}\n")
    #
    #                 if bounds:
    #                     coords = [int(x) for x in bounds.replace('][', ',')
    #                               .replace('[', '')
    #                               .replace(']', '')
    #                               .split(',')]
    #                     x_center = (coords[0] + coords[2]) // 2
    #                     y_center = (coords[1] + coords[3]) // 2
    #
    #                     label = text or desc or resource  # ✅ fix: use proper label
    #                     if not label:
    #                         continue
    #
    #                     if (x_center, y_center) not in seen:
    #                         seen.add((x_center, y_center))
    #                         print(f"{label:30} => adb shell input tap {x_center} {y_center}")
    #         print(f"✅ Converted XML to TXT: {LOCAL_TXT}")
    #
    #     except Exception as e:
    #         print(f"❌ Error converting XML to TXT: {e}")

    def dump_ui_and_convert(self):
    # Step 1: Dump XML hierarchy from device
        DEVICE_FILE = "/sdcard/window_dump.xml"
        LOCAL_FILE = "ui.txt"

        subprocess.run(["adb", "shell", "uiautomator", "dump", DEVICE_FILE], check=True)
        subprocess.run(["adb", "pull", DEVICE_FILE, LOCAL_FILE], check=True)

        with open(LOCAL_FILE, "r", encoding="utf-8") as f:
            xml_data = f.read()

    # Step 2: Parse using regex
        nodes = re.findall(
            r'text="(.*?)".*?resource-id="(.*?)".*?content-desc="(.*?)".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
            xml_data, re.DOTALL
        )

        result_lines = []
        for text, resource, desc, x1, y1, x2, y2 in nodes:
        # Pick a meaningful label: text > desc > resource
            label = text.strip() or desc.strip() or resource.strip()
            if not label:
                continue

        # Center of the bounds
            x_center = (int(x1) + int(x2)) // 2
            y_center = (int(y1) + int(y2)) // 2

            result_lines.append(f"{label:<30} => adb shell input tap {x_center} {y_center}")

    # Step 3: Save final readable format
        with open("ui_parsed.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(result_lines))

        print("✅ Parsed UI saved to ui_parsed.txt")



# Create object and call functions
#cam = camera()
# cam.devices()
# cam.cam_capture()
# cam.image_back()
# cam.open_video()
# cam.video_capture()
# cam.video_back()
# cam.dumpsys_cam()
# cam.logcat_cam()
# cam.cam_nodes()
# cam.cam_flip()
