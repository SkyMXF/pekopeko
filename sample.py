import os
import time

from adb.runner import AdbRunner
from locate.patch import search_patch, check_patch

adb_runner = AdbRunner()
adb_runner.update_devices()
print(adb_runner.device_info)
#adb_runner.tap(pos=(832, 227), dev=list(adb_runner.device_info.keys())[0])
#adb_runner.swipe(src_pos=(800, 350), aim_pos=(400, 300))

adb_runner.screen_shot()

pos = search_patch(
    template_file=os.path.join("resources", "browser.png"),
    screen_file=os.path.join("cache", "emulator-5554.png"),
    threshold=0.8,
    grayscale=True,
    scale_change=False,
    match_first=False
)
print(pos)
#if pos is not None:
#    adb_runner.tap(pos, norm_pos=True)

check_result = check_patch(
    template_file=os.path.join("resources", "browser.png"),
    screen_file=os.path.join("cache", "emulator-5554.png"),
    pos=(0.5075, 0.21),
    threshold=0.8,
    scale_change=True
)
print(check_result)