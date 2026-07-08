import os
import httpx    
from fastapi import FastAPI, Request, Response
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
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
            }
            response = await client.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Errore API POTA (Status {response.status_code})"}
            
            res_data = response.json()
            if isinstance(res_data, list):
                return res_data
            return {"error": "Formato dati POTA non valido (Non è una lista)"}
        except Exception as e:
            return {"error": f"Errore server Python: {str(e)}"}

@app.post("/api/spot")
async def proxy_pota_spot(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            auth_header = request.headers.get("Authorization")
            
            pota_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Origin": "https://pota.app",
                "Referer": "https://pota.app/"
            }
            if auth_header:
                pota_headers["Authorization"] = auth_header

            response = await client.post(
                "https://api.pota.app/spot",
                content=body,
                headers=pota_headers,
                timeout=10
            )
            return Response(content=response.content, status_code=response.status_code, headers={"Content-Type": "application/json"})
        except Exception as e:
            return Response(content=f'{{"success": false, "message": "{str(e)}"}}', status_code=500, headers={"Content-Type": "application/json"})

@app.get("/manifest.json")
def get_manifest():
    if os.path.exists("manifest.json"):
        return FileResponse("manifest.json", media_type="application/json")
    return {"error": "Manifest non trovato"}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato nella root del server</h1>")
