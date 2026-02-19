# hub_service/main.py
import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# --- Configuration ---
HUB_HOST = "0.0.0.0"
HUB_PORT = 8002

app = FastAPI(title="Nami Central Hub")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static UI Serving ---
# Update this path to where your built Angular files live
ui_path = Path(__file__).parent / "ui_dist" 
if ui_path.exists():
    app.mount("/", StaticFiles(directory=str(ui_path), html=True), name="ui")

# --- Socket.IO Event Relays ---
@sio.on("*")
async def catch_all(event, sid, data):
    """
    Relay all incoming events from any client (Nami/Twitch) 
    to all other connected clients (UI/Twitch).
    """
    print(f"[Hub] Relaying event '{event}' from {sid}")
    await sio.emit(event, data, skip_sid=sid)

@sio.event
async def connect(sid, environ):
    print(f"[Hub] Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"[Hub] Client disconnected: {sid}")

if __name__ == "__main__":
    print(f"🚀 Nami Central Hub starting on port {HUB_PORT}...")
    uvicorn.run(socket_app, host=HUB_HOST, port=HUB_PORT)