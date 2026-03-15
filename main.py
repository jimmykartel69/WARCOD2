"""
WARCOD2 - Main Entry Point
============================
Experimental & Personal Use Only

Real-time screen analyzer for Warzone gameplay.
Uses OpenCV for image analysis, PyAutoGUI for screen capture,
pynput for mouse control, and NumPy for image processing.

Usage:
    python main.py

Hotkeys (configurable in config.py):
    F6  - Toggle analysis ON/OFF
    F7  - Toggle overlay display
    F8  - Save screenshot with detections
    F9  - Toggle motion detection mode
    F10 - Exit
"""

import sys
import time
import logging
import cv2
from pynput import keyboard

import config
from screen_analyzer import ScreenAnalyzer
from mouse_controller import MouseController
from overlay import OverlayRenderer


# ─── Logging Setup ─────────────────────────────────────────────────────

def setup_logging():
    """Configure the logging system."""
    log_format = (
        "%(asctime)s │ %(name)-28s │ %(levelname)-7s │ %(message)s"
    )
    handlers = [logging.StreamHandler(sys.stdout)]

    if config.LOG_TO_FILE:
        handlers.append(logging.FileHandler(config.LOG_FILE, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format=log_format,
        handlers=handlers,
    )


# ─── Application ───────────────────────────────────────────────────────

class WarcoDApp:
    """Main application orchestrating all modules."""

    def __init__(self):
        self.logger = logging.getLogger("WARCOD2.App")
        self.analyzer = ScreenAnalyzer()
        self.mouse_ctrl = MouseController()
        self.overlay = OverlayRenderer()
        self.running = True
        self.aim_active = False
        self._aim_key_pressed = False
        
        # Shared results for multi-threading
        self.latest_results = {"ai_detections": [], "fps": 0}
        self.last_frame = None
        
        # Kinetic Tracking (For high frequency smoothness)
        self.last_target_pos = None
        self.target_velocity = (0, 0)
        self.last_update_time = time.time()
        
        self._setup_hotkeys()
        self.logger.info("=" * 60)
        self.logger.info("  WARCOD2 ULTIMATE - Multi-Threaded Engine Enabled")
        self.logger.info("=" * 60)

    def _setup_hotkeys(self):
        """Register global hotkeys using pynput."""
        key_map = {
            config.HOTKEY_TOGGLE_ANALYSIS: self._on_toggle_analysis,
            config.HOTKEY_TOGGLE_OVERLAY: self._on_toggle_overlay,
            config.HOTKEY_TOGGLE_AIM: self._on_toggle_aim,
            config.HOTKEY_SCREENSHOT: self._on_screenshot,
            config.HOTKEY_EXIT: self._on_exit,
        }

        def on_press(key):
            try:
                # Special handle for keys like Caps Lock
                k = ""
                if hasattr(key, 'char') and key.char is not None:
                    k = key.char.lower()
                elif hasattr(key, 'name') and key.name is not None:
                    k = key.name
                else:
                    k = str(key).replace('Key.', '')
                
                # Check for AIM key press
                if k == config.AIM_HOTKEY:
                    self._aim_key_pressed = True

                if k in key_map:
                    key_map[k]()
            except Exception:
                pass

        def on_release(key):
            try:
                k = ""
                if hasattr(key, 'char') and key.char is not None:
                    k = key.char.lower()
                elif hasattr(key, 'name') and key.name is not None:
                    k = key.name
                else:
                    k = str(key).replace('Key.', '')
                    
                if k == config.AIM_HOTKEY:
                    self._aim_key_pressed = False
            except Exception:
                pass

        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        self.logger.info("Hotkeys registered.")

    # ─── Hotkey Callbacks ──────────────────────────────────────────

    def _on_toggle_analysis(self):
        self.analyzer.analysis_enabled = not self.analyzer.analysis_enabled
        state = "ON" if self.analyzer.analysis_enabled else "OFF"
        self.logger.info(f"⚡ Analysis toggled: {state}")

    def _on_toggle_overlay(self):
        self.overlay.toggle()

    def _on_toggle_aim(self):
        config.AIM_ENABLED = not config.AIM_ENABLED
        state = "ON" if config.AIM_ENABLED else "OFF"
        self.logger.info(f"🎯 Aimbot toggled: {state}")

    def _on_aim_key(self):
        # Already handled in Listener
        pass

    def _on_screenshot(self):
        self.logger.info("📸 Saving screenshot...")
        if self.last_frame is not None:
            self.analyzer.save_screenshot(self.last_frame)

    def _on_toggle_motion(self):
        self.analyzer.motion_mode = not self.analyzer.motion_mode
        state = "ON" if self.analyzer.motion_mode else "OFF"
        self.logger.info(f"🔄 Motion detection: {state}")

    def _on_exit(self):
        self.logger.info("🛑 Exit requested.")
        self.running = False

    # ─── Dedicated AI Thread ───────────────────────────────────────

    def _ai_loop(self):
        """Background thread for heavy AI processing."""
        self.logger.info("Background AI Thread started.")
        while self.running:
            if self.analyzer.analysis_enabled:
                frame = self.analyzer.capture_screen()
                self.last_frame = frame
                self.latest_results = self.analyzer.analyze_frame(frame)
            else:
                time.sleep(0.1)

    # ─── Main Controller Loop (High Frequency) ──────────────────────

    def run(self):
        """Main application loop - Logic & HUD."""
        self.logger.info("Starting ULTIMATE controller loop...")
        self.overlay.init_window()

        # Start AI thread
        import threading
        self.ai_thread = threading.Thread(target=self._ai_loop, daemon=True)
        self.ai_thread.start()

        target_fps = 120 # High frequency for cursor and prediction
        target_dt = 1.0 / target_fps

        try:
            while self.running:
                loop_start = time.time()

                # Process aimbot using the latest available AI results
                if config.AIM_ENABLED:
                    self._process_aimbot(self.latest_results)

                # Render overlay based on shared results
                self.overlay.render(self.latest_results)

                # Frame control
                elapsed = time.time() - loop_start
                if elapsed < target_dt:
                    time.sleep(target_dt - elapsed)

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user.")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.shutdown()

    def _process_aimbot(self, results):
        """Ultimate Kinetic Aimbot: Adaptive movement prediction."""
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        if not self._aim_key_pressed:
            self.last_target_pos = None
            self.target_velocity = (0, 0)
            return

        targets = results.get("ai_detections", [])
        cx, cy = self.mouse_ctrl.get_screen_center()
        best_target = None
        min_dist = config.AIM_FOV 

        # We always check for new targets from the latest AI scan
        if targets:
            for target in targets:
                tx, ty = target["head"]
                dist = ((tx - cx)**2 + (ty - cy)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    best_target = (tx, ty)

            if best_target:
                if self.last_target_pos:
                    # Smoothing velocity to avoid twitchy predictions
                    vx = (best_target[0] - self.last_target_pos[0]) / dt
                    vy = (best_target[1] - self.last_target_pos[1]) / dt
                    # Low-pass filter for velocity
                    self.target_velocity = (
                        self.target_velocity[0] * 0.7 + vx * 0.3,
                        self.target_velocity[1] * 0.7 + vy * 0.3
                    )
                self.last_target_pos = best_target
        
        # KINETIC PREDICTION: If AI is slow, we use velocity to 'glide' towards target
        if not best_target and self.last_target_pos and self.target_velocity != (0,0):
            # Predict where target is NOW
            pred_x = self.last_target_pos[0] + self.target_velocity[0] * dt
            pred_y = self.last_target_pos[1] + self.target_velocity[1] * dt
            best_target = (pred_x, pred_y)
            self.last_target_pos = best_target

        if best_target:
            dist_to_center = ((best_target[0] - cx)**2 + (best_target[1] - cy)**2)**0.5
            self.mouse_ctrl.enabled = True 
            self.mouse_ctrl.lerp_towards(int(best_target[0]), int(best_target[1]), dist_to_center)

    def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down...")
        self.overlay.destroy_window()
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
        self.logger.info("Goodbye! 👋")


# ─── Entry Point ───────────────────────────────────────────────────────

def print_banner():
    """Display the startup banner."""
    banner = r"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ██╗    ██╗ █████╗ ██████╗  ██████╗ ██████╗ ██████╗     ║
    ║   ██║    ██║██╔══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗    ║
    ║   ██║ █╗ ██║███████║██████╔╝██║     ██║   ██║██║  ██║    ║
    ║   ██║███╗██║██╔══██║██╔══██╗██║     ██║   ██║██║  ██║    ║
    ║   ╚███╔███╔╝██║  ██║██║  ██║╚██████╗╚██████╔╝██████╔╝    ║
    ║    ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝    ║
    ║                                                          ║
    ║          SCREEN ANALYZER v1.0 - Experimental             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    setup_logging()
    print_banner()

    logger = logging.getLogger("WARCOD2")
    logger.info("Checking dependencies...")

    # Dependency check
    try:
        import cv2
        logger.info(f"  ✓ OpenCV {cv2.__version__}")
    except ImportError:
        logger.error("  ✗ OpenCV not found. Install: pip install opencv-python")
        sys.exit(1)

    try:
        import numpy as np
        logger.info(f"  ✓ NumPy {np.__version__}")
    except ImportError:
        logger.error("  ✗ NumPy not found. Install: pip install numpy")
        sys.exit(1)

    try:
        import pyautogui
        logger.info(f"  ✓ PyAutoGUI {pyautogui.__version__}")
    except ImportError:
        logger.error("  ✗ PyAutoGUI not found. Install: pip install pyautogui")
        sys.exit(1)

    try:
        import pynput
        logger.info("  ✓ pynput installed")
    except ImportError:
        logger.error("  ✗ pynput not found. Install: pip install pynput")
        sys.exit(1)

    logger.info("All dependencies OK.\n")

    app = WarcoDApp()
    app.run()


if __name__ == "__main__":
    main()
