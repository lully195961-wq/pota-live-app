import os
import httpx
import telnetlib
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

# Il tuo identificativo ufficiale per accedere alla rete dei cluster
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
    
    # Conversione della frequenza da kHz (es. 7047) a MHz (es. 7.047)
    try:
        freq_khz = float(data.get("frequency", 0))
        freq_mhz = freq_khz / 1000.0 if freq_khz > 1000 else freq_khz
    except Exception:
        return {"success": False, "message": "Frequenza inserita non valida."}

    if not activator or freq_mhz == 0 or not reference:
        return {"success": False, "message": "Mancano dati obbligatori (Attivatore, Frequenza o Referenza)."}

    # Costruzione del comando DX Cluster corretto: DX [frequenza] [attivatore] [commenti con referenza]
    # Esempio: DX 7.047 IK6LMB POTA IT-1031 FT8
    comment_string = f"POTA {reference} {mode} {comments}".strip()
    cluster_command = f"DX {freq_mhz:.3f} {activator} {comment_string}\r\n"

    # Configurazione del server DX Cluster scelto
    CLUSTER_HOST = "ik4icz.dyndns.org"
    CLUSTER_PORT = 8000

    try:
        # Apertura connessione Telnet immediata
        tn = telnetlib.Telnet(CLUSTER_HOST, CLUSTER_PORT, timeout=5)
        
        # Attesa del prompt d'ingresso "login:" per inviare il tuo callsign
        tn.read_until(b"login:", timeout=3)
        tn.write(f"{CLUSTER_LOGIN_CALLSIGN}\r\n".encode('ascii'))
        
        # Aspetta una frazione di secondo per l'accettazione del login e invia lo spot
        tn.read_very_eager()
        tn.write(cluster_command.encode('ascii'))
        
        # Chiusura pulita della sessione sul cluster
        tn.write(b"quit\r\n")
        tn.close()
        
        return {"success": True, "message": f"✓ Spot inviato con successo tramite {CLUSTER_HOST}!"}
        
    except Exception as e:
        return {"success": False, "message": f"Errore di connessione al Cluster: {str(e)}"}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato nel server</h1>")
