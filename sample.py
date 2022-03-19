from adb.runner import AdbRunner
from locate.ocr import get_text

adb_runner = AdbRunner()
adb_runner.update_devices()
print(adb_runner.device_info)
#adb_runner.tap(pos=(832, 227), dev=list(adb_runner.device_info.keys())[0])
#adb_runner.swipe(src_pos=(800, 350), aim_pos=(400, 300))

adb_runner.screen_shot()

output = get_text(list(adb_runner.device_info.keys())[0])
print(output)