# WARCOD2 - ULTIMATE AI SCREEN ANALYZER 🦅🎯

![Status](https://img.shields.io/badge/Status-Ultimate_Edition-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![AI](https://img.shields.io/badge/AI-YOLOv8-red)
![Engine](https://img.shields.io/badge/Engine-Multi--Threaded-orange)

**WARCOD2 Ultimate** is a high-performance, AI-driven screen analysis engine designed for real-time player detection and tracking. Built with a decentralized multi-threaded architecture, it offers professional-grade precision and a tactical HUD overlay.

---

## 💎 CORE FEATURES

### 🚀 High-Frequency Multi-Threaded Engine
- **Decentralized Threads**: AI inference runs in a dedicated background thread, decoupled from the main control loop.
- **120Hz Control Loop**: Mouse movement and HUD rendering run at ultra-high frequency, ensuring zero input lag.
- **MSS Turbo Capture**: High-speed screen grabbing with thread-isolated Win32 handles.

### 🎯 Predictive Kinetic Tracking (v2)
- **Trajectory Prediction**: Uses velocity vectors to predict target movement between AI scans.
- **60 FPS Feeling**: Even if the AI runs at 20 FPS, the cursor movement is interpolated to feel like a smooth 60+ FPS experience.
- **Adaptive Magnetism**: Strong snap-on for close targets, surgical smoothing for long-range precision.

### 🦅 Advanced AI Analysis
- **YOLOv8 Optimized**: Supports both `yolov8n` (Nano - Speed) and `yolov8s` (Small - Precision).
- **FP16 Inference**: Automated Half-Precision (FP16) compute for CUDA-enabled GPUs, doubling inference speeds.
- **Human Ratio Filtering**: Intelligent shape analysis to ignore menu icons, weapons, or static objects.

### 📊 Tactical HUD (Premium Overlay)
- **Corner-Box Design**: Minimalistic military-grade target framing.
- **Reactive Crosshair**: Real-time visual feedback when a target is successfully locked.
- **System Telemetry**: On-screen display of Engine FPS, detection counts, and module status.

---

## ⚙️ CONFIGURATION & TUNING

Everything is controlled via `config.py`. Key parameters for peak performance:

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `AI_MODEL_PATH` | Model | `yolov8n.pt` (Speed) or `yolov8s.pt` (Elite) |
| `AI_CONFIDENCE` | 0.0 - 1.0 | Detection threshold (0.20 - 0.35 recommended) |
| `AI_CAPTURE_SIZE` | Pixels | 640 (standard) or 1024 (long range) |
| `AIM_LOCK_SPEED` | Multiplier| Power of the magnetic lock |
| `AIM_SMOOTHING` | 0.0 - 1.0 | Softness of movement (Adaptive in Ultimate) |

---

## ⌨️ HOTKEYS

- **[INSERT]**: Toggle Screen Analysis (ON/OFF).
- **[F6]**: Toggle Aimbot Feature.
- **[F7]**: Toggle Tactical HUD visibility.
- **[F8]**: Save detailed screenshot with AI detections.
- **[F10]**: Emergency Exit (Clean Shutdown).
- **[CAPS LOCK]**: **Hold** to engage the Magnetic Target Lock.

---

## 🛠️ INSTALLATION

1. **Prerequisites**: Python 3.10+ and an NVIDIA GPU with CUDA.
2. **Dependencies**:
   ```bash
   pip install opencv-python numpy mss ultralytics torch torchvision pyautogui pynput
   ```
3. **Run**:
   ```bash
   python main.py
   ```
   *Always run as Administrator for proper mouse control and overlay priority.*

---

## ⚠️ DISCLAIMER
This software is intended for **Experimental & Personal Evaluation Use Only**. Using it in online environments may violate the terms of service of third-party software. Use responsibly.

---
**WARCOD2 ULTIMATE // PRO ENGINEERING**
