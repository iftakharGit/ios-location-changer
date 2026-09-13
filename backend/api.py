import math
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel, Field
from backend.device_manager import device_manager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

class JoystickState:
    def __init__(self):
        self.active = False
        self.heading = 0.0
        self.speed = 5.0

joy_state = JoystickState()

def move_lat_lng(lat, lng, heading_deg, distance_m):
    R = 6378137
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)
    heading_rad = math.radians(heading_deg)
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance_m / R) +
        math.cos(lat_rad) * math.sin(distance_m / R) * math.cos(heading_rad)
    )
    new_lng_rad = lng_rad + math.atan2(
        math.sin(heading_rad) * math.sin(distance_m / R) * math.cos(lat_rad),
        math.cos(distance_m / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    return math.degrees(new_lat_rad), math.degrees(new_lng_rad)

async def joystick_loop():
    while True:
        if joy_state.active and device_manager.current_lat is not None and device_manager.current_lng is not None:
            distance_m = joy_state.speed * 0.1
            new_lat, new_lng = move_lat_lng(
                device_manager.current_lat, 
                device_manager.current_lng, 
                joy_state.heading, 
                distance_m
            )
            device_manager.set_location(new_lat, new_lng)
        await asyncio.sleep(0.1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(joystick_loop())
    # Prevent premature garbage collection
    setattr(app, 'joystick_task', task)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

static_dir = os.path.join(get_base_path(), 'static')
template_dir = os.path.join(get_base_path(), 'templates')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

try:
    with open(os.path.join(template_dir, "index.html"), "r") as f:
        html_content = f.read()
except Exception:
    html_content = "UI not found"

@app.get("/", response_class=HTMLResponse)
async def index():
    return html_content

class LocationRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class SpeedRequest(BaseModel):
    speed: float

class JoystickRequest(BaseModel):
    action: str
    heading: float = 0.0

@app.get("/api/status")
async def get_status():
    return {
        "connected": device_manager.connected,
        "intent": device_manager.intent_to_connect,
        "error": device_manager.last_error,
        "lat": device_manager.current_lat,
        "lng": device_manager.current_lng
    }

@app.post("/api/connect")
async def connect_device():
    device_manager.connect()
    return {"status": "success"}

@app.post("/api/disconnect")
async def disconnect_device():
    joy_state.active = False
    device_manager.disconnect()
    return {"status": "success"}

@app.post("/api/set_location")
async def set_location(req: LocationRequest):
    joy_state.active = False
    device_manager.set_location(req.lat, req.lng)
    return {"status": "success"}

@app.post("/api/stop")
async def stop_location():
    joy_state.active = False
    device_manager.clear_location()
    return {"status": "success"}

@app.post("/api/speed")
async def set_speed(req: SpeedRequest):
    joy_state.speed = req.speed
    return {"status": "success", "speed": joy_state.speed}

@app.post("/api/joystick")
async def set_joystick(req: JoystickRequest):
    if req.action == "start":
        joy_state.active = True
        joy_state.heading = req.heading
    elif req.action == "update":
        joy_state.heading = req.heading
    elif req.action == "stop":
        joy_state.active = False
        
    return {
        "status": "success", 
        "lat": device_manager.current_lat, 
        "lng": device_manager.current_lng
    }
