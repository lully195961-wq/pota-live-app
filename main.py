import os
import httpx
import telnetlib3
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLUSTER_LOGIN_CALLSIGN = "IK6LMB"

@app.get("/api/spots")
async def get_pota_spots():
    url = "https://api.pota.app/spot"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

@app.post("/api/spot")
async def send_pota_spot(request: Request):
    data = await request.json()
    activator = data.get("activator", "").upper().strip()
    reference = data.get("reference", "").upper().strip()
    mode = data.get("mode", "").upper().strip()
    comments = data.get("comments", "").strip()
    
    try:
        freq_khz = float(data.get("frequency", 0))
        freq_mhz = freq_khz / 1000.0 if freq_khz > 1000 else freq_khz
    except:
        return {"success": False, "message": "Frequenza non valida."}

    if not activator or freq_mhz == 0 or not reference:
        return {"success": False, "message": "Dati obbligatori mancanti."}

    # Sintassi standardizzata per i cluster
    comment_string = f"POTA-{reference} {mode} {comments}".strip()
    cluster_command = f"DX {freq_mhz:.3f} {activator} {comment_string}\r\n"

    try:
        reader, writer = await telnetlib3.open_connection('ik4icz.dyndns.org', 8000)
        await reader.readuntil(b'login:')
        writer.write(f"{CLUSTER_LOGIN_CALLSIGN}\r\n")
        writer.write(cluster_command)
        await writer.drain()
        writer.close()
        return {"success": True, "message": "Spot inviato con successo!"}
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

@app.get("/")
def read_root():
    return FileResponse("index.html")
