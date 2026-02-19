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
ui_path = Path(__file__).parent / "ui_dist"
if ui_path.exists():
    app.mount("/", StaticFiles(directory=str(ui_path), html=True), name="ui")


# --- Connection Events ---

@sio.event
async def connect(sid, environ):
    print(f"[Hub] Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"[Hub] Client disconnected: {sid}")


# --- Explicit Relay Handlers ---
# These forward each event from whichever service sent it
# to all other connected clients.

@sio.on("twitch_message")
async def relay_twitch_message(sid, data):
    print(f"[Hub] twitch_message from {sid}: {str(data)[:80]}")
    await sio.emit("twitch_message", data, skip_sid=sid)

@sio.on("event")
async def relay_event(sid, data):
    print(f"[Hub] event from {sid}: {str(data)[:80]}")
    await sio.emit("event", data, skip_sid=sid)

@sio.on("bot_reply")
async def relay_bot_reply(sid, data):
    print(f"[Hub] bot_reply from {sid}: {str(data)[:80]}")
    await sio.emit("bot_reply", data, skip_sid=sid)

@sio.on("director_state")
async def relay_director_state(sid, data):
    await sio.emit("director_state", data, skip_sid=sid)

@sio.on("vision_context")
async def relay_vision_context(sid, data):
    await sio.emit("vision_context", data, skip_sid=sid)

@sio.on("spoken_word_context")
async def relay_spoken_word_context(sid, data):
    await sio.emit("spoken_word_context", data, skip_sid=sid)

@sio.on("audio_context")
async def relay_audio_context(sid, data):
    await sio.emit("audio_context", data, skip_sid=sid)

@sio.on("event_scored")
async def relay_event_scored(sid, data):
    await sio.emit("event_scored", data, skip_sid=sid)

@sio.on("ai_context_suggestion")
async def relay_ai_context_suggestion(sid, data):
    await sio.emit("ai_context_suggestion", data, skip_sid=sid)

# UI → Director control events (forwarded to director)
@sio.on("set_streamer")
async def relay_set_streamer(sid, data):
    await sio.emit("set_streamer", data, skip_sid=sid)

@sio.on("set_manual_context")
async def relay_set_manual_context(sid, data):
    await sio.emit("set_manual_context", data, skip_sid=sid)

@sio.on("set_streamer_lock")
async def relay_set_streamer_lock(sid, data):
    await sio.emit("set_streamer_lock", data, skip_sid=sid)

@sio.on("set_context_lock")
async def relay_set_context_lock(sid, data):
    await sio.emit("set_context_lock", data, skip_sid=sid)


if __name__ == "__main__":
    print(f"🚀 Nami Central Hub starting on port {HUB_PORT}...")
    uvicorn.run(socket_app, host=HUB_HOST, port=HUB_PORT)