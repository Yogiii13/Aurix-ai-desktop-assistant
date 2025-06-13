import subprocess
import logging
from ctypes import cast, POINTER
import os
import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        self._init_volume_control()

    def _init_volume_control(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.error(f"Failed to initialize volume control: {e}")
            self.volume = None

    def set_volume(self, level):
        """
        Set the system volume level (0-100).
        """
        if self.volume is None:
            return "Volume control is not available."

        try:
            level = max(0, min(100, level))  # Ensure level is between 0 and 100
            self.volume.SetMasterVolumeLevelScalar(level / 100, None)
            return f"Volume set to {level}%"
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return "Failed to set volume."

    def get_volume(self):
        """
        Get the current system volume level (0-100).
        """
        if self.volume is None:
            return "Volume control is not available."

        try:
            current_volume = round(self.volume.GetMasterVolumeLevelScalar() * 100)
            return f"Current volume is {current_volume}%"
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return "Failed to get volume."

    def set_brightness(self, level):
        """
        Set the screen brightness level (0-100).
        """
        try:
            level = max(0, min(100, level))  # Ensure level is between 0 and 100
            sbc.set_brightness(level)
            return f"Brightness set to {level}%"
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return "Failed to set brightness."

    def get_brightness(self):
        """
        Get the current screen brightness level (0-100).
        """
        try:
            current_brightness = sbc.get_brightness()[0]
            return f"Current brightness is {current_brightness}%"
        except Exception as e:
            logger.error(f"Failed to get brightness: {e}")
            return "Failed to get brightness."

    def mute_volume(self):
        """
        Mute the system volume.
        """
        if self.volume is None:
            return "Volume control is not available."

        try:
            self.volume.SetMute(1, None)
            return "Volume muted"
        except Exception as e:
            logger.error(f"Failed to mute volume: {e}")
            return "Failed to mute volume."

    def unmute_volume(self):
        """
        Unmute the system volume.
        """
        if self.volume is None:
            return "Volume control is not available."

        try:
            self.volume.SetMute(0, None)
            return "Volume unmuted"
        except Exception as e:
            logger.error(f"Failed to unmute volume: {e}")
            return "Failed to unmute volume."
            
    def shutdown_system(self, delay=30):
        """
        Shutdown the system with a delay (in seconds).
        """
        try:
            # Use shutdown command with a delay to give user time to cancel if needed
            subprocess.run(['shutdown', '/s', '/t', str(delay)], check=True)
            return f"System will shutdown in {delay} seconds. Use 'cancel shutdown' to abort."
        except Exception as e:
            logger.error(f"Failed to shutdown system: {e}")
            return "Failed to shutdown system."
            
    def restart_system(self, delay=30):
        """
        Restart the system with a delay (in seconds).
        """
        try:
            subprocess.run(['shutdown', '/r', '/t', str(delay)], check=True)
            return f"System will restart in {delay} seconds. Use 'cancel restart' to abort."
        except Exception as e:
            logger.error(f"Failed to restart system: {e}")
            return "Failed to restart system."
            
    def cancel_shutdown(self):
        """
        Cancel a scheduled shutdown or restart.
        """
        try:
            subprocess.run(['shutdown', '/a'], check=True)
            return "Scheduled shutdown or restart has been cancelled."
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {e}")
            return "Failed to cancel shutdown."
            
    def sleep_system(self):
        """
        Put the system to sleep.
        """
        try:
            # Use powercfg to put system to sleep
            subprocess.run(['powercfg', '/hibernate', 'off'], check=True)
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            return "Putting system to sleep..."
        except Exception as e:
            logger.error(f"Failed to put system to sleep: {e}")
            return "Failed to put system to sleep."
            
    def lock_screen(self):
        """
        Lock the screen.
        """
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Screen locked."
        except Exception as e:
            logger.error(f"Failed to lock screen: {e}")
            return "Failed to lock screen."
            
    def get_system_info(self):
        """
        Get basic system information.
        """
        try:
            import platform
            import psutil
            
            system_info = {
                "system": platform.system(),
                "version": platform.version(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "memory_total": round(psutil.virtual_memory().total / (1024**3), 2),  # GB
                "memory_available": round(psutil.virtual_memory().available / (1024**3), 2),  # GB
                "disk_usage": round(psutil.disk_usage('/').percent, 2),  # Percent
                "cpu_usage": psutil.cpu_percent(interval=1)  # Percent
            }
            
            info_str = (
                f"System: {system_info['system']} {system_info['version']}\n"
                f"Processor: {system_info['processor']} ({system_info['architecture']})\n"
                f"Memory: {system_info['memory_available']}GB available of {system_info['memory_total']}GB total\n"
                f"Disk Usage: {system_info['disk_usage']}%\n"
                f"CPU Usage: {system_info['cpu_usage']}%"
            )
            
            return info_str
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return "Failed to retrieve system information."