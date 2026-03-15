"""
WARCOD2 - Game-Ready Mouse Controller
=======================================
Direct Win32 SendInput implementation for bypassing Raw Input.
"""

import time
import math
import logging
import ctypes
import win32api
import win32con

import config

logger = logging.getLogger("WARCOD2.MouseController")

# Structure for SendInput (Needed for 3D Games)
PUL = ctypes.POINTER(ctypes.c_ulong)
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class MouseController:
    """Pro-grade mouse controller using Direct SendInput."""

    def __init__(self):
        self.smoothing = config.MOUSE_SMOOTHING
        self.speed_factor = config.MOUSE_SPEED_FACTOR
        self.deadzone = config.MOUSE_DEADZONE
        self.enabled = False
        
        # Screen center is the reference for 3D games
        self.sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.center_x = self.sw // 2
        self.center_y = self.sh // 2
        
        logger.info("MouseController initialized (GAME-READY Mode).")

    @property
    def position(self) -> tuple:
        return win32api.GetCursorPos()

    def get_screen_center(self) -> tuple:
        """Required for main.py coordinate calculations."""
        return (self.center_x, self.center_y)

    def _send_input(self, dx, dy, flags):
        """Low-level SendInput call."""
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(int(dx), int(dy), 0, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def move_relative(self, dx: int, dy: int):
        """Relative move using SendInput."""
        if not self.enabled:
            return
        self._send_input(dx, dy, win32con.MOUSEEVENTF_MOVE)

    def lerp_towards(self, target_x: int, target_y: int, dist: float):
        """
        Ultimate Adaptive Lock: Pure Magnetism.
        """
        if not self.enabled:
            return

        dx = target_x - self.center_x
        dy = target_y - self.center_y

        # If very close, we snap at 100% to ensure the head is locked
        if dist < 50:
            smoothing = 0.0 # Instant Snap
        elif dist < 200:
            smoothing = 0.05 # Fierce
        else:
            smoothing = 0.15 # Fine for distance

        factor = (1.0 - smoothing) * config.AIM_LOCK_SPEED
        
        # Power Boost: Ensure minimum movement for sticky feel
        if factor > 1.0: factor = 1.0
            
        move_x = int(dx * factor)
        move_y = int(dy * factor)

        # Force at least 1 pixel movement if delta exists (Anti-Stuck)
        if dx != 0 and move_x == 0: move_x = 1 if dx > 0 else -1
        if dy != 0 and move_y == 0: move_y = 1 if dy > 0 else -1

        self.move_relative(move_x, move_y)

    def click(self, button: str = "left"):
        """Perform a hardware-level click."""
        if not self.enabled:
            return
        if button == "left":
            self._send_input(0, 0, win32con.MOUSEEVENTF_LEFTDOWN)
            time.sleep(0.01)
            self._send_input(0, 0, win32con.MOUSEEVENTF_LEFTUP)
        else:
            self._send_input(0, 0, win32con.MOUSEEVENTF_RIGHTDOWN)
            time.sleep(0.01)
            self._send_input(0, 0, win32con.MOUSEEVENTF_RIGHTUP)

    def toggle(self):
        self.enabled = not self.enabled
        state = "ENABLED" if self.enabled else "DISABLED"
        logger.info(f"Mouse control {state}")
        return self.enabled
