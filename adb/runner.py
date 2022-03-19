import os
import re

class CmdRunningError(Exception):

    def __init__(self,info):
        super().__init__(self)
        self.info = info

    def __str__(self):
        return self.info

class AdbRunner(object):

    def __init__(self) -> None:
        self.device_info = {}
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # init adb server
        #self._run_cmd("adb kill-server && adb server", get_result=False)

        # get device info
        self.update_devices()
        self.get_resolution()
    
    def _run_cmd(self, cmd, get_result=True):
        if get_result:
            result = os.popen(cmd)
            result = result.read().splitlines()
            return result
        else:
            code = os.system(cmd)
            if code != 0:
                raise CmdRunningError("'%s' return %d"%(cmd, code))
    
    def update_devices(self):
        # update self.devices_info

        devices_output = self._run_cmd("adb devices")

        if devices_output[0] != "List of devices attached":
            raise CmdRunningError("Get unexpected result '%s' running 'adb devices'."%(devices_output[0]))
        
        if len(devices_output) == 2:
            return
        
        for _, dev_info in self.device_info.items():
            dev_info["available"] = False

        for line in devices_output[1:]:
            dev_name = line.split("\t")[0]
            if dev_name == "":
                continue
            if not (dev_name in self.device_info.keys()):
                self.device_info[dev_name] = {}
            
            self.device_info[dev_name]["available"] = True
    
    def get_resolution(self, dev=None):
        # get device resolution

        def build_resolution_cmd(device):
            return "adb -s %s shell wm size"%(device)
        
        pattern = re.compile(r'\d+')
        devices = list(self.device_info.keys()) if dev is None else [dev]
        for dev in devices:
            resolution_output = self._run_cmd(build_resolution_cmd(dev))[0]
            w, h = pattern.findall(resolution_output)
            self.device_info[dev]["height"] = h
            self.device_info[dev]["width"] = w
    
    def screen_shot(self, dev=None):
        # get screen shot

        def build_screencap_cmd(device, output):
            return "adb -s %s exec-out screencap -p > %s"%(device, output)

        devices = list(self.device_info.keys()) if dev is None else [dev]
        for dev in devices:
            self._run_cmd(
                build_screencap_cmd(
                    dev,
                    os.path.join(self.cache_dir, "%s.png"%(dev))
                )
            )

    def tap(self, pos, dev=None):
        # tap once

        def build_tap_cmd(device, pos):
            return "adb -s %s shell input tap %d %d"%(device, pos[0], pos[1])
        
        devices = list(self.device_info.keys()) if dev is None else [dev]
        for dev in devices:
            self._run_cmd(build_tap_cmd(dev, pos))

    def multi_tap(self, dev, pos, times, interval=50):
        # tap several times
        raise NotImplementedError("Multiple tap not implemented yet.")

    def swipe(self, src_pos, aim_pos, time=100, dev=None):
        # swipe

        def build_swipe_cmd(device, src_pos, aim_pos, time):
            return "adb -s %s shell input swipe %d %d %d %d %d"%(
                device, src_pos[0], src_pos[1], aim_pos[0], aim_pos[1], time
            )
        
        devices = list(self.device_info.keys()) if dev is None else [dev]
        for dev in devices:
            self._run_cmd(build_swipe_cmd(dev, src_pos, aim_pos, time))