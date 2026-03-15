"""
WARCOD2 - Screen Analyzer Module
=================================
Experimental & Personal Use Only

Core module for capturing and analyzing the screen in real-time using
OpenCV and NumPy. Provides color detection, contour analysis, edge
detection, and motion tracking capabilities.
"""

import time
import logging
import numpy as np
import cv2
import mss
import torch
import win32api
import win32con
from ultralytics import YOLO

import config

logger = logging.getLogger("WARCOD2.ScreenAnalyzer")


class ScreenAnalyzer:
    """Real-time screen capture and image analysis engine."""

    def __init__(self):
        self.region = config.CAPTURE_REGION
        self.sct = None # Will be initialized in the correct thread
        
        # Monitor setup for Center-only capture (Ultra fast)
        self.sw = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.sh = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # FOCUS SCAN: Shifted UP to ignore player's body (hands/legs)
        self.crop_size = config.AI_CAPTURE_SIZE
        self.monitor = {
            "top": (self.sh // 2) - int(self.crop_size * 0.8), # Scan mostly ABOVE center
            "left": (self.sw - self.crop_size) // 2,
            "width": self.crop_size,
            "height": self.crop_size
        }
        # Clamp top to 0 and ensure we don't scan too low
        if self.monitor["top"] < 0: self.monitor["top"] = 0
        # Clamp top to 0
        if self.monitor["top"] < 0: self.monitor["top"] = 0
        
        self.offset_x = self.monitor["left"]
        self.offset_y = self.monitor["top"]

        self.prev_frame = None
        self.frame_count = 0
        self.fps = 0.0
        self._last_fps_time = time.time()
        self._fps_frame_count = 0
        self.detections = []
        self.analysis_enabled = True
        
        # Load YOLO AI Model with Hardware Acceleration
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading AI Model: {config.AI_MODEL_PATH} on {device}...")
        self.model = YOLO(config.AI_MODEL_PATH).to(device)
        logger.info(f"AI Model loaded on {device}.")

    # ─── Screen Capture ────────────────────────────────────────────────

    def capture_screen(self) -> np.ndarray:
        """Capture the screen at high speed using MSS (Thread-safe)."""
        # LAZY INIT: mss must be initialized in the thread that uses it
        if not hasattr(self, 'sct') or self.sct is None:
            self.sct = mss.mss()
            
        # Grab the data
        sct_img = self.sct.grab(self.monitor)
        # Convert to numpy array (BGRA) and then to BGR
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        
        self.frame_count += 1
        self._update_fps()
        return frame

    def _update_fps(self):
        """Calculate rolling FPS."""
        self._fps_frame_count += 1
        elapsed = time.time() - self._last_fps_time
        if elapsed >= 1.0:
            self.fps = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._last_fps_time = time.time()

    # ─── Preprocessing ─────────────────────────────────────────────────

    @staticmethod
    def preprocess(frame: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur to reduce noise."""
        return cv2.GaussianBlur(frame, config.BLUR_KERNEL_SIZE, 0)

    @staticmethod
    def to_hsv(frame: np.ndarray) -> np.ndarray:
        """Convert BGR frame to HSV color space."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    @staticmethod
    def to_gray(frame: np.ndarray) -> np.ndarray:
        """Convert BGR frame to grayscale."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ─── Color Detection ──────────────────────────────────────────────

    def detect_ai(self, frame: np.ndarray) -> list:
        """Analyze frame using YOLO AI model - Elite Optimized."""
        detections = []
        
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True

        # Run inference on the center crop (ULTIMATE SPEED)
        results = self.model.predict(
            source=frame,
            conf=config.AI_CONFIDENCE,
            iou=0.45, 
            classes=config.AI_CLASSES,
            verbose=False,
            imgsz=config.AI_CAPTURE_SIZE,
            half=True if torch.cuda.is_available() else False, # FP16 Turbo Speed
            agnostic_nms=True,
            augment=False, # Faster
            stream=False 
        )

        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            for box in boxes:
                # Bounding box coordinates (Local to crop)
                lx1, ly1, lx2, ly2 = box.xyxy[0].tolist()
                lw, lh = lx2 - lx1, ly2 - ly1
                
                # HUMAN RATIO FILTER: A player is taller than wide
                aspect_ratio = lw / lh
                if aspect_ratio > 1.2: # Allow more horizontal flexibility (moving targets)
                    continue
                
                # MIN SIZE FILTER: Relaxed for extreme distance 🦅
                if lw < 2 or lh < 5:
                    continue

                # Global coordinates (Target for mouse)
                gx1, gy1 = lx1 + self.offset_x, ly1 + self.offset_y
                gcx, gcy = gx1 + lw / 2, gy1 + lh / 2
                
                # Head estimation: Slightly higher for forehead/face lock
                head_x, head_y = gcx, gy1 + (lh * 0.12)
                detections.append({
                    "label": "Player",
                    "bbox": (int(gx1), int(gy1), int(lw), int(lh)),
                    "center": (int(gcx), int(gcy)),
                    "head": (int(head_x), int(head_y)),
                    "area": int(lw * lh),
                    "color_bgr": (0, 0, 255),
                })

        self.detections = detections
        return detections

    def detect_colors(self, frame: np.ndarray) -> list:
        """
        Detect regions matching configured color profiles.
        Returns a list of detection dicts:
          { 'label', 'bbox': (x,y,w,h), 'center': (cx,cy), 'area', 'color_bgr' }
        """
        detections = []
        blurred = self.preprocess(frame)
        hsv = self.to_hsv(blurred)

        for profile_name, profile in config.COLOR_PROFILES.items():
            lower = np.array(profile["lower"], dtype=np.uint8)
            upper = np.array(profile["upper"], dtype=np.uint8)

            mask = cv2.inRange(hsv, lower, upper)

            # Morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, config.MORPH_KERNEL_SIZE
            )
            mask = cv2.dilate(mask, kernel, iterations=config.MORPH_ITERATIONS)
            mask = cv2.erode(mask, kernel, iterations=config.MORPH_ITERATIONS)

            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            for contour in contours:
                area = cv2.contourArea(contour)
                if config.MIN_CONTOUR_AREA <= area <= config.MAX_CONTOUR_AREA:
                    x, y, w, h = cv2.boundingRect(contour)
                    cx, cy = x + w // 2, y + h // 2
                    detections.append({
                        "label": profile["label"],
                        "profile": profile_name,
                        "bbox": (x, y, w, h),
                        "center": (cx, cy),
                        "area": area,
                        "color_bgr": profile["color_bgr"],
                    })

        self.detections = detections
        return detections

    # ─── Shape Analysis ───────────────────────────────────────────────

    @staticmethod
    def analyze_contour_shape(contour) -> dict:
        """Analyze a contour's shape properties."""
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        extent = float(area) / (w * h) if (w * h) > 0 else 0
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0

        # Circularity
        circularity = 0
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)

        return {
            "area": area,
            "perimeter": perimeter,
            "bbox": (x, y, w, h),
            "aspect_ratio": aspect_ratio,
            "extent": extent,
            "solidity": solidity,
            "circularity": circularity,
        }

    # ─── Template Matching ────────────────────────────────────────────

    @staticmethod
    def match_template(
        frame: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.8,
    ) -> list:
        """
        Find all occurrences of a template in the frame.
        Returns list of (x, y, w, h) bounding boxes.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = gray_template.shape[:2]

        result = cv2.matchTemplate(
            gray_frame, gray_template, cv2.TM_CCOEFF_NORMED
        )
        locations = np.where(result >= threshold)

        matches = []
        for pt in zip(*locations[::-1]):
            matches.append((pt[0], pt[1], w, h))

        return matches

    # ─── Full Analysis Pipeline ───────────────────────────────────────

    def analyze_frame(self, frame: np.ndarray) -> dict:
        """
        Run the full analysis pipeline on a single frame.
        Returns a dict with all analysis results.
        """
        results = {
            "frame_number": self.frame_count,
            "fps": round(self.fps, 1),
            "color_detections": [],
            "timestamp": time.time(),
        }

        if not self.analysis_enabled:
            return results

        # Run AI detection (Players/Enemies)
        results["ai_detections"] = self.detect_ai(frame)
        
        # Color-based detection disabled for performance and clarity
        results["color_detections"] = []

        return results

    # ─── Utility ──────────────────────────────────────────────────────

    def get_closest_detection(self, screen_center: tuple) -> dict | None:
        """Return the detection closest to the given screen center point."""
        if not self.detections:
            return None

        cx, cy = screen_center
        closest = None
        min_dist = float("inf")

        for det in self.detections:
            dx = det["center"][0] - cx
            dy = det["center"][1] - cy
            dist = np.sqrt(dx * dx + dy * dy)
            if dist < min_dist:
                min_dist = dist
                closest = det

        return closest

    def save_screenshot(self, frame: np.ndarray, filename: str = None):
        """Save a screenshot with detection overlays."""
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"

        annotated = self.draw_detections(frame.copy())
        cv2.imwrite(filename, annotated)
        logger.info(f"Screenshot saved: {filename}")

    def draw_detections(self, frame: np.ndarray) -> np.ndarray:
        """Draw all current detections on the frame."""
        for det in self.detections:
            x, y, w, h = det["bbox"]
            color = det["color_bgr"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            label = f"{det['label']} ({det['area']}px)"
            cv2.putText(
                frame, label, (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1,
            )
            # Draw center crosshair
            cx, cy = det["center"]
            cv2.drawMarker(
                frame, (cx, cy), color,
                cv2.MARKER_CROSS, 10, 1,
            )

        return frame
