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

POTA_USERNAME = "ik6lmb@libero.it"
POTA_PASSWORD = "Marilin1!"

@app.get("/api/spots")
async def get_pota_spots():
    url = "https://api.pota.app/spot"
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            response = await client.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"Errore Server POTA (Codice {response.status_code})"}
                
            return response.json()
        except Exception as e:
            return {"error": f"Errore di connessione Python: {str(e)}"}

@app.post("/api/spot")
async def send_pota_spot(request: Request):
    data = await request.json()
    
    login_url = "https://api.pota.app/login"
    login_payload = {"username": POTA_USERNAME, "password": POTA_PASSWORD}
    
    # Header identici a quelli di un browser moderno per evitare i blocchi 403
    headers_login = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://pota.app",
        "Referer": "https://pota.app/"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Eseguiamo il login inviando il payload JSON corretto
            login_response = await client.post(login_url, json=login_payload, headers=headers_login)
            
            if login_response.status_code != 200:
                return {"success": False, "message": f"Login fallito: {login_response.status_code}"}
                
            token_data = login_response.json()
            pota_jwt_token = token_data.get("token") or token_data.get("jwt")
            
            if not pota_jwt_token:
                return {"success": False, "message": "Token non trovato nella risposta."}
            
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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Origin": "https://pota.app",
                "Referer": "https://pota.app/"
            }
            
            response = await client.post(spot_url, json=pota_payload, headers=headers_spot)
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Spot inviato!"}
            return {"success": False, "message": f"Errore invio spot: {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato</h1>")
