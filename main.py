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

# IL TUO NUOVO ACCESS TOKEN INSERITO CON SUCCESSO
POTA_ACCESS_TOKEN = "eyJraWQiOiI4Wm9SbnhvdER4QkNmVlFCQjNSU1dlWGZyWE9YMzFzY05FRFJheVVYa1NnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzM2RkNWEwZi0yYTA4LTQ1YjUtOWIxZC0yMWU3OGYwM2Q1ODIiLCJjb2duaXRvOmdyb3VwcyI6WyJVcGxvYWQiXSwiaXNzIjoiaHR0cHM6Ly9jb2duaXRvLWlkcC51cy1lYXN0LTIuYW1hem9uYXdzLmNvbS91cy1lYXN0LTJfbkE1alowa2xoIiwidmVyc2lvbiI6MiwiY2xpZW50X2lkIjoiN2hsdXFjdDBuMm5ja2liN2k3c2Q1NzUzb2EiLCJldmVudF9pZCI6ImY5MTA3YmIxLTBlOWQtNGMxNi1iNTg1LWMzMjNlZmVlZjU2NSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4gcGhvbmUgb3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhdXRoX3RpbWUiOjE3ODM0MjUzOTcsImV4cCI6MTc4MzQyODk5NywiaWF0IjoxNzgzNDI1Mzk3LCJqdGkiOiJiOTNhMGM5ZC0zNDUwLTQ2YjUtYmEzYi01MjU2ZjljMWVkMmUiLCJ1c2VybmFtZSI6IjMzZGQ1YTBmLTJhMDgtNDViNS05YjFkLTIxZTc4ZjAzZDU4MiJ9.Hc1ZIbWyHhQmjp1N_Tar0oZ1b46FG8u1XGm7PNoGcjL03dRe95qrzxtnhPWM6Iasl_qpdbo67pmauogI20LHVxlhOvfZet6QSxNAf13su3Zkxk7_829QZBE2hmg5ngJDWUhDueOi1KfMzJhuIHlF0uA5ju14TEDzq7FDcPwTXcqgFXXkz1X84RnvMIW_0vtsi_qJtOkGe04rZJ8JrT5kRhYpbP0B5V02Bzvp2GXJI-4gcch4kclwLsBtAq4rtc7_7klTsM7Ukx96se9Dbo3EmwW42eaFQ__H1mT0xhIxX9jwDu4G4MUmXf582i6Zzs0mrBvt1DLRh2yQMW2WlBsO7A"

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
    
    if not POTA_ACCESS_TOKEN or POTA_ACCESS_TOKEN.startswith("INCOLLA"):
        return {"success": False, "message": "Errore: Token non configurato nel server backend."}
        
    async with httpx.AsyncClient() as client:
        try:
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
                "Authorization": f"Bearer {POTA_ACCESS_TOKEN}", 
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*"
            }
            
            response = await client.post(spot_url, json=pota_payload, headers=headers_spot)
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Spot inviato con successo!"}
            
            try:
                err_detail = response.json()
                msg = err_detail.get("message", f"Codice {response.status_code}")
            except:
                msg = f"Codice {response.status_code}"
                
            return {"success": False, "message": f"Rifiutato da POTA: {msg}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato</h1>")
