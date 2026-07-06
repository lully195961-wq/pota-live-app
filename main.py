import os
import httpx    
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

# CREDENZIALI POTA
POTA_USERNAME = "ik6lmb@libero.it"
POTA_PASSWORD = "Marilin1!"

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
    
    login_url = "https://api.pota.app/auth/login"
    login_payload = {
        "username": POTA_USERNAME, 
        "password": POTA_PASSWORD
    }
    
    headers_login = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Effettua il login esplicito con gli header JSON corretti
            login_response = await client.post(login_url, json=login_payload, headers=headers_login)
            
            if login_response.status_code != 200:
                return {"success": False, "message": f"Login fallito (Codice {login_response.status_code}): {login_response.text}"}
                
            token_data = login_response.json()
            pota_jwt_token = token_data.get("token")
            
            if not pota_jwt_token:
                return {"success": False, "message": "Token non trovato nella risposta di login di POTA."}
            
            activator = data.get("activator", "").upper().strip()
            spotter = data.get("spotter", "").upper().strip()
            reference = data.get("reference", "").upper().strip()
            mode = data.get("mode", "").upper().strip()
            
            freq_khz = float(data.get("frequency", 0))
            freq_mhz = freq_khz / 1000.0 if freq_khz > 1000 else freq_khz

            spot_url = "https://api.pota.app/spot"
            pota_payload = {
                "activator": activator,
                "spotter": spotter,
                "frequency": freq_mhz,
                "mode": mode,
                "reference": reference,
                "comments": data.get("comments", "")
            }
            
            headers_spot = {
                "Authorization": f"Bearer {pota_jwt_token}", 
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = await client.post(spot_url, json=pota_payload, headers=headers_spot)
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Spot inviato!"}
            return {"success": False, "message": f"Errore POTA {response.status_code}: {response.text}"}
            
        except Exception as e:
            return {"success": False, "message": f"Errore di connessione: {str(e)}"}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato nel server</h1>")
