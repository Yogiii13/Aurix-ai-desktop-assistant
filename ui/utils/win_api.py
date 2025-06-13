import ctypes
from ctypes import wintypes
import win32gui
import win32con

# Taskbar progress indicator (Windows 7+)
def set_taskbar_progress(hwnd, state, progress=0):
    """
    Set the taskbar progress indicator for the specified window.
    
    Args:
        hwnd: The window handle
        state: The progress state (0: no progress, 1: indeterminate, 2: normal, 3: error, 4: paused)
        progress: The progress value (0-100, only used when state is 2)
    """
    try:
        taskbar = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AIAssistant")
        taskbar = ctypes.windll.shell32.CoCreateInstance(
            ctypes.c_uint64(0x56FDF344FDBCB848), None,
            ctypes.c_uint32(1), ctypes.c_uint64(0x0000000011cf0000),
            ctypes.byref(ctypes.c_void_p())
        )
        taskbar.HrInit()
        taskbar.SetProgressState(hwnd, state)
        if state == 2:  # TBPF_NORMAL
            taskbar.SetProgressValue(hwnd, progress, 100)
    except Exception as e:
        print(f"Failed to set taskbar progress: {e}")

# Dark title bar (Windows 10/11)
def enable_dark_mode(hwnd: wintypes.HWND):
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, 
        DWMWA_USE_IMMERSIVE_DARK_MODE, 
        ctypes.byref(ctypes.c_int(1)), 
        ctypes.sizeof(ctypes.c_int)
    )

def set_dark_title_bar(hwnd):
    """
    Enable dark mode for the title bar of the specified window.
    
    Args:
        hwnd: The window handle
    """
    try:
        dwm_api = ctypes.windll.dwmapi
        value = ctypes.c_int(2)
        dwm_api.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
    except Exception as e:
        print(f"Failed to set dark title bar: {e}")

def set_window_blur(hwnd):
    """
    Enable the Aero Glass effect (blur) for the specified window.
    
    Args:
        hwnd: The window handle
    """
    try:
        blur_behind = win32gui.BLURBEHIND()
        blur_behind.dwFlags = win32con.DWM_BB_ENABLE
        blur_behind.fEnable = True
        blur_behind.hRgnBlur = None
        ctypes.windll.dwmapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(blur_behind))
    except Exception as e:
        print(f"Failed to set window blur: {e}")

def set_window_corners(hwnd, radius=10):
    """
    Set rounded corners for the specified window.
    
    Args:
        hwnd: The window handle
        radius: The corner radius in pixels
    """
    try:
        DWMWCP_ROUND = 2
        DWMWCP_ROUNDSMALL = 3
        value = ctypes.c_int(DWMWCP_ROUND if radius > 5 else DWMWCP_ROUNDSMALL)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 33, ctypes.byref(value), ctypes.sizeof(value)
        )
    except Exception as e:
        print(f"Failed to set window corners: {e}")

def set_window_shadow(hwnd):
    """
    Enable window shadow for the specified window.
    
    Args:
        hwnd: The window handle
    """
    try:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.CS_DROPSHADOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    except Exception as e:
        print(f"Failed to set window shadow: {e}")
