import os
import subprocess
import logging
import winreg
import json
import psutil
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AppLauncher:
    def __init__(self):
        """Initialize the AppLauncher with common Windows applications and registry apps."""
        self.app_paths = {}
        self._load_installed_apps()
        self._add_common_windows_apps()

    def _load_installed_apps(self):
        """Load installed applications from Windows registry."""
        try:
            # Load from cache if available
            cache_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', 'app_paths.json')
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    self.app_paths = json.load(f)
                logger.info(f"Loaded {len(self.app_paths)} apps from cache")
                return
                
            # If no cache, scan registry
            self._scan_registry_for_apps()
            
            # Save to cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.app_paths, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error loading installed apps: {e}")
            # Ensure we have at least common apps
            self._add_common_windows_apps()

    def _scan_registry_for_apps(self):
        """Scan Windows registry for installed applications."""
        try:
            # Common registry paths for installed applications
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    self._process_registry_key(key)
                except Exception as e:
                    logger.debug(f"Error accessing registry path {reg_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scanning registry: {e}")

    def _process_registry_key(self, key):
        """Process a registry key to extract application paths."""
        try:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    try:
                        app_path = winreg.QueryValue(subkey, None)
                        if app_path and app_path.endswith('.exe'):
                            app_name = os.path.basename(app_path).lower().replace('.exe', '')
                            self.app_paths[app_name] = app_path
                    except:
                        pass
                        
                    winreg.CloseKey(subkey)
                    i += 1
                except WindowsError:
                    break
        except Exception as e:
            logger.debug(f"Error processing registry key: {e}")

    def _add_common_windows_apps(self):
        """Add common Windows applications that might not be in registry."""
        common_apps = {
            # System apps
            "notepad": r"C:\Windows\System32\notepad.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "control panel": r"C:\Windows\System32\control.exe",
            "task manager": r"C:\Windows\System32\taskmgr.exe",
            "file explorer": r"C:\Windows\explorer.exe",
            "settings": r"ms-settings:",  # Special URI for Windows Settings
            
            # Microsoft apps
            "edge": r"microsoft-edge:",  # URI for Microsoft Edge
            
            # Microsoft Office apps with common installation paths
            "word": self._find_office_app("WINWORD.EXE"),
            "excel": self._find_office_app("EXCEL.EXE"),
            "powerpoint": self._find_office_app("POWERPNT.EXE"),
            "outlook": self._find_office_app("OUTLOOK.EXE"),
            
            # Common browsers
            "chrome": r"chrome.exe",
            "firefox": r"firefox.exe",
            "brave": r"brave.exe",
            
            # Media apps
            "media player": r"C:\Program Files\Windows Media Player\wmplayer.exe",
            "photos": r"ms-photos:",  # URI for Photos app
            
            # Store apps
            "store": r"ms-windows-store:",  # URI for Microsoft Store
        }
        
        for app_name, app_path in common_apps.items():
            if app_name not in self.app_paths and app_path:
                self.app_paths[app_name] = app_path
                
        logger.info(f"Added common Windows apps")

    def _find_office_app(self, exe_name):
        """Find Microsoft Office application path."""
        # Common Office installation paths
        office_paths = [
            r"C:\Program Files\Microsoft Office\root\Office16",
            r"C:\Program Files\Microsoft Office\Office16",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16",
            r"C:\Program Files (x86)\Microsoft Office\Office16",
            r"C:\Program Files\Microsoft Office\root\Office15",
            r"C:\Program Files\Microsoft Office\Office15",
            r"C:\Program Files (x86)\Microsoft Office\root\Office15",
            r"C:\Program Files (x86)\Microsoft Office\Office15",
        ]
        
        for path in office_paths:
            full_path = os.path.join(path, exe_name)
            if os.path.exists(full_path):
                return full_path
                
        # Try to find in Program Files
        for root_dir in [r"C:\Program Files", r"C:\Program Files (x86)"]:
            for root, dirs, files in os.walk(root_dir):
                if exe_name in files:
                    return os.path.join(root, exe_name)
        
        return None

    def launch_app(self, app_name):
        """Launch the specified application."""
        app_name = app_name.lower()
        
        # Check if app exists in our dictionary
        if app_name in self.app_paths:
            try:
                app_path = self.app_paths[app_name]
                
                # Handle special URIs
                if app_path and (app_path.startswith("ms-") or ":" in app_path):
                    os.startfile(app_path)
                    logger.info(f"Launched URI application: {app_name}")
                    return f"Successfully launched {app_name}."
                
                # Handle executable paths
                if app_path and app_path.endswith(".exe"):
                    subprocess.Popen(app_path)
                elif app_path:
                    subprocess.Popen([app_path])
                else:
                    return f"Failed to launch {app_name}. Path not found."
                    
                logger.info(f"Launched application: {app_name}")
                return f"Successfully launched {app_name}."
            except Exception as e:
                logger.error(f"Error launching {app_name}: {e}")
                return f"Failed to launch {app_name}. Error: {str(e)}"
        else:
            # Try to find similar app names for better user experience
            similar_apps = self._find_similar_apps(app_name)
            if similar_apps:
                suggestions = ", ".join(similar_apps[:3])
                return f"Application '{app_name}' not found. Did you mean: {suggestions}?"
            return f"Application '{app_name}' not found."

    def get_installed_apps(self):
        """Return a list of installed applications."""
        return list(self.app_paths.keys())
        
    def close_app(self, app_name):
        """Close the specified application."""
        app_name = app_name.lower()
        
        # Map of app names to possible process names (some apps have multiple processes)
        process_map = {
            "word": ["winword.exe"],
            "excel": ["excel.exe"],
            "powerpoint": ["powerpnt.exe"],
            "outlook": ["outlook.exe"],
            "notepad": ["notepad.exe"],
            "chrome": ["chrome.exe", "googlechrome.exe"],
            "firefox": ["firefox.exe"],
            "brave": ["brave.exe"],
            "edge": ["msedge.exe"],
            "calculator": ["calculator.exe"],
            "cmd": ["cmd.exe"],
            "task manager": ["taskmgr.exe"],
            "file explorer": ["explorer.exe"],
            "visual studio code": ["code.exe"],
            "visual studio": ["devenv.exe"],
            "spotify": ["spotify.exe"],
            "discord": ["discord.exe", "Update.exe"],
            "teams": ["teams.exe", "ms-teams.exe"],
            "zoom": ["zoom.exe", "zoomwindows.exe"],
            "skype": ["skype.exe", "lync.exe"],
            "vlc": ["vlc.exe"],
        }
        
        try:
            # Get process names to check
            process_names = []
            if app_name in process_map:
                process_names = process_map[app_name]
            else:
                # Try to derive process name from app name or path
                if app_name in self.app_paths:
                    path = self.app_paths[app_name]
                    if path.endswith('.exe'):
                        process_names = [os.path.basename(path).lower()]
                
                # If we still don't have a process name, use app name + .exe
                if not process_names:
                    process_names = [f"{app_name}.exe"]
            
            logger.debug(f"Looking for processes: {process_names}")
            
            # Try to find and close the processes
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info['name'].lower()
                
                # Check if this process matches any of our target names
                if any(target.lower() == proc_name for target in process_names):
                    try:
                        logger.debug(f"Attempting to terminate process: {proc_name} (PID: {proc.info['pid']})")
                        proc.terminate()
                        
                        # Wait for process to terminate (with timeout)
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            # If timeout, try to kill the process forcefully
                            logger.debug(f"Process {proc_name} did not terminate, attempting to kill")
                            proc.kill()
                        
                        closed = True
                        logger.info(f"Closed process: {proc_name}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                        logger.error(f"Error terminating {proc_name}: {e}")
            
            if closed:
                return f"Successfully closed {app_name}."
            else:
                # Try a more aggressive search for the process
                for proc in psutil.process_iter(['pid', 'name']):
                    proc_name = proc.info['name'].lower()
                    
                    # Check if any of our target names is a substring of the process name
                    if any(target.lower() in proc_name for target in process_names):
                        try:
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                            except psutil.TimeoutExpired:
                                proc.kill()
                            
                            closed = True
                            logger.info(f"Closed process with partial match: {proc_name}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                            logger.error(f"Error terminating {proc_name}: {e}")
                
                if closed:
                    return f"Successfully closed {app_name}."
                else:
                    # Try using taskkill as a last resort (Windows only)
                    if os.name == 'nt':
                        for process_name in process_names:
                            try:
                                subprocess.run(['taskkill', '/F', '/IM', process_name], 
                                              check=False, 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE)
                                closed = True
                                logger.info(f"Closed {process_name} using taskkill")
                            except Exception as e:
                                logger.error(f"Error using taskkill for {process_name}: {e}")
                    
                    if closed:
                        return f"Successfully closed {app_name}."
                    else:
                        return f"Application '{app_name}' is not running or could not be closed."
                
        except Exception as e:
            logger.error(f"Error closing {app_name}: {e}")
            return f"Failed to close {app_name}. Error: {str(e)}"

    def _find_similar_apps(self, app_name):
        """Find similar app names based on substring matching."""
        return [name for name in self.app_paths.keys() 
                if app_name in name or name in app_name]
    