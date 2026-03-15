AI_MODEL_PATH = "yolov8s.pt"    # Nano Model pour fluidité max
AI_CONFIDENCE = 0.20            # Sensibilité accrue pour la longue portée
AI_CAPTURE_SIZE = 1024          # Zone de scan élargie (Multiple de 32)
AI_CLASSES = [0]                # Joueurs

# ─── Screen Capture Settings ───────────────────────────────────────────
CAPTURE_REGION = None     # Full Screen
CAPTURE_FPS = 120         # Target max (le script tournera au max possible)
DISPLAY_SCALE = 1.0       

# ─── Color Detection Ranges (HSV) ─────────────────────────────────────
# We keep only specific markers to avoid noise.
COLOR_PROFILES = {
    "enemy_red": {
        "lower": (0, 150, 150),
        "upper": (5, 255, 255),
        "label": "Red Marker",
        "color_bgr": (0, 0, 255),
    },
    "enemy_red2": {
        "lower": (175, 150, 150),
        "upper": (180, 255, 255),
        "label": "Red Marker 2",
        "color_bgr": (0, 0, 255),
    },
    # White removed (too much noise)
    "highlight_yellow": {
        "lower": (25, 150, 150),
        "upper": (35, 255, 255),
        "label": "Yellow Marker",
        "color_bgr": (0, 255, 255),
    },
}

# ─── Detection Parameters ─────────────────────────────────────────────
MIN_CONTOUR_AREA = 150          # Minimum contour area to consider (pixels²)
MAX_CONTOUR_AREA = 50000        # Maximum contour area to consider
BLUR_KERNEL_SIZE = (5, 5)       # Gaussian blur kernel size
MORPH_KERNEL_SIZE = (3, 3)      # Morphological operation kernel size
MORPH_ITERATIONS = 2            # Morphological dilation/erosion iterations

# ─── Edge Detection ───────────────────────────────────────────────────
CANNY_THRESHOLD_LOW = 50
CANNY_THRESHOLD_HIGH = 150

# ─── Motion Detection ─────────────────────────────────────────────────
MOTION_THRESHOLD = 30           # Pixel difference threshold
MOTION_MIN_AREA = 500           # Minimum area for motion regions

# ─── Mouse Controller ─────────────────────────────────────────────────
MOUSE_SMOOTHING = 0.3           # Smoothing factor (0 = instant, 1 = very slow)
MOUSE_SPEED_FACTOR = 1.0        # Speed multiplier for mouse movement
MOUSE_DEADZONE = 1              # Précision chirurgicale

# ─── Overlay Settings ─────────────────────────────────────────────────
OVERLAY_OPACITY = 1.0           # Transparent window opacity (0-1)
OVERLAY_TRANSPARENT = True      # Make window background transparent
OVERLAY_CLICK_THROUGH = True    # Make window click-through
OVERLAY_FONT_SCALE = 0.6        # Font scale for labels
OVERLAY_THICKNESS = 2           # Line/rectangle thickness
OVERLAY_SHOW_FPS = True         # Show FPS counter
OVERLAY_SHOW_DETECTIONS = True  # Show detection count

# ─── Logging ───────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"              # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True              # Write logs to file
LOG_FILE = "warcod2_analyzer.log"

# ─── Aimbot / Lock Settings ───────────────────────────────────────────
AIM_ENABLED = True              # Global toggle for aim assist
AIM_HOTKEY = "caps_lock"        # Key to hold for locking
AIM_FOV = 1080                   # FOV Large pour accrocher de loin
AIM_SMOOTHING = 0.1            # Snap instantané
AIM_TARGET_OFFSET = 0.15        # Headshot parfait (Front/Haut du visage)
AIM_LOCK_SPEED = 5.0            # Vitesse magnétique Pro
# ─── Hotkeys ───────────────────────────────────────────────────────────
HOTKEY_TOGGLE_ANALYSIS = "insert"   # Toggle analysis on/off
HOTKEY_TOGGLE_OVERLAY = "f7"        # Toggle overlay display
HOTKEY_TOGGLE_AIM = "f6"            # Toggle aimbot feature
HOTKEY_SCREENSHOT = "f8"            # Save screenshot with detections
HOTKEY_EXIT = "f10"                 # Exit application
