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

@app.post("/api/spot")
async def send_pota_spot(request: Request):
    data = await request.json()
    
    login_url = "https://api.pota.app/auth/login"
    login_payload = {
        "username": POTA_USERNAME,
        "password": POTA_PASSWORD
    }
    
    async with httpx.AsyncClient() as client:
        try:
            login_response = await client.post(login_url, json=login_payload)
            if login_response.status_code != 200:
                return {"success": False, "message": f"Errore Login POTA: {login_response.text}"}
                
            token_data = login_response.json()
            pota_jwt_token = token_data.get("token") or token_data.get("accessToken", "")
            if not pota_jwt_token:
                return {"success": False, "message": "Impossibile recuperare il token."}
            
            spot_url = "https://api.pota.app/spot"
            pota_payload = {
                "activator": data.get("activator", "").upper(),
                "spotter": data.get("spotter", "").upper(),
                "frequency": int(data.get("frequency", 0)),
                "reference": data.get("reference", "").upper(),
                "comments": data.get("comments", "")
            }
            
            headers = {
                "Authorization": f"Bearer {pota_jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(spot_url, json=pota_payload, headers=headers)
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Spot inviato su POTA con successo!"}
            else:
                return {"success": False, "message": f"Errore server POTA: {response.text}"}
                
        except Exception as e:
            return {"success": False, "message": f"Errore di rete: {str(e)}"}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato nel server</h1>")
