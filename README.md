# 🌍 iOS Location Changer (V2)

![CI/CD Pipeline](https://github.com/iftakharGit/ios-location-changer/actions/workflows/ci-cd.yml/badge.svg)
![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)
![macOS Support](https://img.shields.io/badge/os-macOS-silver.svg)

A premium, open-source macOS desktop application for overriding the GPS location of iOS 17+ devices—**no jailbreak required**. 

Built entirely on modern Python (FastAPI + pymobiledevice3) and PyWebView, this tool leverages Apple's official Developer Disk Image (CoreDevice) to establish a secure userspace tunnel, allowing you to seamlessly teleport, walk, or drive around the globe.

---

## ✨ Features

* 🗺️ **Interactive Mapping:** Point-and-click teleportation using a beautiful Leaflet map.
* 🕹️ **Real-Time Joystick:** Use your keyboard's `W A S D` keys to walk naturally around the map.
* 🚀 **Auto-App Launching:** Automatically wake your iPhone and launch specific apps (like Apple Maps or Pokémon GO) the exact millisecond the spoofing tunnel connects.
* 📍 **Drag-and-Drop GPX Loader:** Drag any `.gpx` hiking or driving route onto the window to instantly load and simulate the path.
* 🏎️ **Dynamic Speed Engine:** Seamlessly slide your movement speed from a 5mph "Walk" to a 40mph "Drive" mid-route without stuttering.
* 🛰️ **Dynamic Map Layers:** Instantly toggle between standard street views, Esri high-resolution Satellite imagery, and topographical Terrain.
* 🎨 **Native UI:** Enjoy a gorgeous macOS "frosted glass" interface (Vibrancy) built with Tailwind CSS.

---

## 🚀 Getting Started (For End Users)

You do not need to install Python or know how to code to use this application!

1. Go to the [Releases Tab](../../releases/latest).
2. Download the latest `Location_Changer_macOS.zip`.
3. Unzip the file and double-click `Location Changer.app`.
4. Plug in your iPhone via USB, ensure **Developer Mode** is enabled in your iOS Privacy settings, and click **Connect**!

---

## 🛠️ Development Setup (For Developers)

iOS Location Changer uses a strict MVC architecture separating the FastAPI backend from the pure ES6 JavaScript frontend.

### Prerequisites
* macOS (Apple Silicon or Intel)
* Python 3.14+
* Xcode Command Line Tools (`xcode-select --install`)

### Installation
```bash
# Clone the repository
git clone https://github.com/iftakharGit/ios-location-changer.git
cd ios-location-changer

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Compiling the App
To build your own standalone `.app` bundle using PyInstaller:
```bash
pyinstaller --clean --windowed --name "Location Changer" \
  --add-data "templates:templates" --add-data "static:static" \
  --collect-all uvicorn --collect-all fastapi app.py --noconfirm
```
*(Note: A GitHub Actions CI/CD pipeline is already configured in `.github/workflows/ci-cd.yml` to automatically lint, test, and compile the app for you on every push!)*

---

## ⚖️ Disclaimer
*This software is provided for educational and testing purposes only. The developer assumes no liability for accounts banned by third-party applications or services resulting from the use of this tool.*

---

## 📜 Acknowledgments & Third-Party Licenses

This application is made possible thanks to the incredible work of the open-source community. The following libraries are bundled with or utilized by this software:

* **[pymobiledevice3](https://github.com/doronz88/pymobiledevice3)** - Copyright (c) Doron Z. (MIT License)
* **[FastAPI](https://fastapi.tiangolo.com/)** - Copyright (c) 2018 Sebastián Ramírez (MIT License)
* **[pywebview](https://pywebview.flowrl.com/)** - Copyright (c) 2014-2024 Roman Sirokov (BSD 3-Clause License)
* **[Leaflet.js](https://leafletjs.com/)** - Copyright (c) 2010-2023, Vladimir Agafonkin / CloudMade (BSD 2-Clause License)
* **[Tailwind CSS](https://tailwindcss.com/)** - Copyright (c) Tailwind Labs, Inc. (MIT License)

*All third-party trademarks and trade names belong to their respective owners.*
