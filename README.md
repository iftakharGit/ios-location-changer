# iOS Location Changer (V2.1 - Production Ready)

A commercial-grade, fully local iOS location spoofer designed for Apple Silicon macOS and modern iOS (17+) devices. 

This application bypasses traditional GPS dongles by establishing an Apple `CoreDevice` RemotePairing tunnel over USB using `pymobiledevice3`, manipulating the iOS Developer Mode Location Simulation service.

## 🚀 Key Features & Security
- **Pure Userspace Tunnel:** Bypasses macOS Sandbox restrictions and `remoted` privilege issues by handling the entire iOS 17 networking stack in pure Python.
- **Joystick Movement:** WASD directional controls synchronized at 100ms for video-game smooth gliding.
- **Constant-Velocity Route Simulation:** Uses Delta-Time math to calculate exact distances across waypoints regardless of CPU throttling.
- **Strict Data Validation:** Incoming coordinates are strictly bounded by Pydantic validators (-90 to 90 lat, -180 to 180 lng) to prevent device crashing.
- **Thread-Safe Architecture:** Powered by `FastAPI` and an `asyncio.Queue` state manager to ensure perfect thread safety. All globals have been encapsulated into OOP states (`JoystickState`, `DeviceManager`) to eliminate race conditions.
- **Active Health-Checking:** Instead of hardcoded sleep delays, the launcher uses active socket health checks to dynamically bind to safe network ports and wait for the ASGI server to boot.

---

## 🛠 Architecture
* **Frontend:** HTML, TailwindCSS, ES6 JavaScript Modules (Map, Joystick, API handlers). Polling loops are strictly guarded with in-flight flags.
* **Backend:** FastAPI (ASGI Server), `uvicorn` background thread locked securely behind strict CORS (`127.0.0.1` only).
* **Hardware Bridge:** `pymobiledevice3` (DVT Provider & Location Simulation).
* **Desktop Wrapper:** `pywebview` serving the local FastAPI instance on a dynamically allocated port.

---

## 💻 Developer Setup

### 1. Prerequisites
- **macOS** (Apple Silicon recommended)
- **Python 3.10+**
- **iPhone on iOS 16/17+** with **Developer Mode Enabled** (Settings > Privacy & Security > Developer Mode).

### 2. Installation
Dependencies are strictly pinned in `requirements.txt` to guarantee reproducible builds.

```bash
# Clone or open the repository directory
cd "Location changer app"

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install strictly pinned dependencies
pip install -r requirements.txt
```

### 3. Running Locally for Development
Run the application directly via Python. Hot-reloading the UI is as simple as refreshing the webview, but backend changes require restarting the script.
```bash
python app.py
```

### 4. Compiling the Production `.app` Bundle
To package the application into a standalone macOS `.app` that can be dragged into the Applications folder, use PyInstaller. 

We aggressively bundle `uvicorn` and `fastapi` hidden imports to ensure the ASGI server boots correctly inside the macOS Sandbox:

```bash
source venv/bin/activate

pyinstaller --clean --windowed --name "Location Changer" \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --collect-all uvicorn \
  --collect-all fastapi \
  app.py --noconfirm
```

The resulting application will be located at `dist/Location Changer.app`.

---

## 📁 Project Structure
```text
.
├── app.py                      # Pywebview launcher, Dynamic Ports & Active Health Checks
├── backend/
│   ├── api.py                  # FastAPI router, CORS, Pydantic guards, and Joystick loop
│   └── device_manager.py       # OOP state manager and pymobiledevice3 Asyncio Queue
├── static/
│   └── js/
│       ├── api.js              # Fetch API wrappers
│       ├── joystick.js         # WASD vector logic and Status polling
│       └── map.js              # Leaflet mapping, Layer caching, and Delta-Time math
├── templates/
│   └── index.html              # Tailwind UI layout (cached in memory on startup)
├── tools/                      
│   └── spoofer.py              # Legacy diagnostic CLI scripts (excluded from production bundle)
├── requirements.txt            # Pinned Python dependencies
└── dist/                       # PyInstaller output directory
```

## ⚠️ Known Behaviors
- **Audio Routing:** Because this utilizes Apple's RemotePairing network interface, macOS may occasionally think the iPhone is plugged in for "Continuity Camera" and route the iPhone's audio to the Mac. To disable this, turn off **Continuity Camera** in your iPhone's AirPlay & Handoff settings.
