"""
WARCOD2 - Overlay Renderer Module (Tkinter Version)
====================================================
Experimental & Personal Use Only

Uses Tkinter for a truly transparent, hardware-accelerated overlay
that sits on top of the game without a grey background.
"""

import tkinter as tk
import os
import logging
import time

if os.name == 'nt':
    import win32gui
    import win32con
    import win32api

import config

logger = logging.getLogger("WARCOD2.Overlay")


class OverlayRenderer:
    """Renders a truly transparent HUD using Tkinter."""

    def __init__(self):
        self.visible = True
        self.root = None
        self.canvas = None
        self._window_initialized = False
        self._last_update = time.time()
        logger.info("OverlayRenderer (Tkinter) initialized.")

    def init_window(self):
        """Build the transparent Tkinter window."""
        self.root = tk.Tk()
        self.root.title("WARCOD2_OVERLAY")
        
        # Window attributes
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.config(bg="black")
        self.root.lift() # Force to front
        
        # Full screen scaling
        sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.root.geometry(f"{sw}x{sh}+0+0")

        # Canvas
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # Force initial update so we can find the HWND
        self.root.update()

        if os.name == 'nt':
            # Use FindWindow with the specific title to get the right HWND
            hwnd = win32gui.FindWindow(None, "WARCOD2_OVERLAY")
            if hwnd:
                self._make_click_through(hwnd)
            else:
                logger.error("Could not find HWND for overlay.")

        self._window_initialized = True
        logger.info(f"Overlay Window {sw}x{sh} at (0,0) initialized.")

    def _make_click_through(self, hwnd):
        """Use Win32 API to make the window ignore all mouse input."""
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        # Layered + Transparent (Click-through)
        new_style = ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.root.deiconify()
        else:
            self.root.withdraw()
        return self.visible

    def render(self, analysis_results: dict):
        """Update the tactical HUD based on AI results."""
        if not self.visible or not self.canvas:
            self.root.update()
            return

        # 1. Clear previous frame
        self.canvas.delete("all")

        # 2. Draw AI Detections (Players ONLY)
        detections = analysis_results.get("ai_detections", [])
        for det in detections:
            x, y, w, h = det["bbox"]
            hx, hy = det["head"]
            
            # TACTICAL BOX (Corner based for better visibility)
            s = int(w * 0.2) # Corner length
            # Red glow effect
            color = "#FF0000"
            # Draw 4 corners instead of a full rectangle for 'Pro' look
            self.canvas.create_line(x, y, x+s, y, fill=color, width=2)
            self.canvas.create_line(x, y, x, y+s, fill=color, width=2)
            
            self.canvas.create_line(x+w-s, y, x+w, y, fill=color, width=2)
            self.canvas.create_line(x+w, y, x+w, y+s, fill=color, width=2)
            
            self.canvas.create_line(x, y+h-s, x, y+h, fill=color, width=2)
            self.canvas.create_line(x, y+h, x+s, y+h, fill=color, width=2)
            
            self.canvas.create_line(x+w-s, y+h, x+w, y+h, fill=color, width=2)
            self.canvas.create_line(x+w, y+h-s, x+w, y+h, fill=color, width=2)

            # Precision Head point (Small dot)
            self.canvas.create_oval(hx-2, hy-2, hx+2, hy+2, fill="#FFFF00", outline="")

        # 4. HUD Stats
        self._draw_hud(analysis_results)

        # 5. Crosshair
        self._draw_crosshair(len(detections) > 0)

        # Update window
        self.root.update()

    def _draw_hud(self, results):
        # Top-left minimalistic BAR
        self.canvas.create_rectangle(20, 20, 230, 45, fill="#000000", outline="#00FF00", width=1)
        self.canvas.create_text(30, 32, text="WARCOD2 // ULTIMATE", fill="#00FF00", anchor="w", font=("Courier", 10, "bold"))
        
        # System Stats (Floating)
        fps = results.get('fps', 0)
        ai_count = len(results.get("ai_detections", []))
        
        status_color = "#00FF00" if config.AIM_ENABLED else "#888888"
        status_text = "LOCK: ACTIVE" if config.AIM_ENABLED else "LOCK: IDLE"
        
        y = 55
        self.canvas.create_text(30, y, text=f"ENGINE FPS: {fps:.1f}", fill="white", anchor="w", font=("Arial", 9))
        y += 15
        self.canvas.create_text(30, y, text=f"TARGETS: {ai_count}", fill="#FF0000", anchor="w", font=("Arial", 9, "bold"))
        y += 15
        self.canvas.create_text(30, y, text=status_text, fill=status_color, anchor="w", font=("Arial", 9, "bold"))

    def _draw_crosshair(self, has_target):
        sw = self.root.winfo_width()
        sh = self.root.winfo_height()
        cx, cy = sw // 2, sh // 2
        
        color = "#00FF00" # Green by default
        if has_target and config.AIM_ENABLED:
            color = "#FFFF00" # Yellow when locking
            
        s = 8
        g = 3 # Gap
        # Tactical crosshair with gap
        self.canvas.create_line(cx-s-g, cy, cx-g, cy, fill=color, width=2)
        self.canvas.create_line(cx+g, cy, cx+s+g, cy, fill=color, width=2)
        self.canvas.create_line(cx, cy-s-g, cx, cy-g, fill=color, width=2)
        self.canvas.create_line(cx, cy+g, cx, cy+s+g, fill=color, width=2)
        
        # Small center dot
        self.canvas.create_oval(cx-1, cy-1, cx+1, cy+1, fill=color, outline="")

    def destroy_window(self):
        if self.root:
            self.root.destroy()
