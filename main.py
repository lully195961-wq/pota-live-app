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
    spotter = data.get("spotter", "").upper().strip()
    reference = data.get("reference", "").upper().strip()
    mode = data.get("mode", "").upper().strip()
    comments = data.get("comments", "").strip()
    
    # Conversione frequenza da kHz (es. 7047) a MHz (es. 7.047) richiesta dai cluster
    try:
        freq_khz = float(data.get("frequency", 0))
        freq_mhz = freq_khz / 1000.0 if freq_khz > 1000 else freq_khz
    except Exception:
        return {"success": False, "message": "Frequenza non valida."}

    if not spotter or not activator or freq_mhz == 0:
        return {"success": False, "message": "Mancano i dati obbligatori (Spotter, Attivatore o Frequenza)."}

    # Configurazione della stringa dello spot secondo lo standard DX Cluster
    # Sintassi: DX SPOTTER FREQ_MHZ ACTIVATOR COMMENTI_E_REFERENZA
    # Esempio: DX IK6LMB 7.047 K2L POTA US-2157 FT8
    comment_string = f"POTA {reference} {mode} {comments}".strip()
    cluster_command = f"DX {spotter} {freq_mhz:.3f} {activator} {comment_string}\r\n"

    # INVIO TRAMITE DX CLUSTER (Bypassa i blocchi AWS di POTA)
    CLUSTER_HOST = "dxc.ik5xct.it"
    CLUSTER_PORT = 7300

    try:
        # Connessione Telnet rapida al cluster
        tn = telnetlib.Telnet(CLUSTER_HOST, CLUSTER_PORT, timeout=5)
        
        # Aspetta la richiesta del CallSign dal cluster ed effettua il login
        tn.read_until(b"login:", timeout=3)
        tn.write(f"{spotter}\r\n".encode('ascii'))
        
        # Invia il comando dello spot
        tn.write(cluster_command.encode('ascii'))
        tn.write(b"quit\r\n")
        tn.close()
        
        return {"success": True, "message": f"Spot inviato al Cluster {CLUSTER_HOST}! Apparirà a breve su POTA."}
        
    except Exception as e:
        return {"success": False, "message": f"Errore connessione Cluster: {str(e)}"}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato nel server</h1>")
