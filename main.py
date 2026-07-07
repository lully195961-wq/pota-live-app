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

# IL TUO TOKEN ATTIVO INSERITO CON SUCCESSO
POTA_ACCESS_TOKEN = "eyJraWQiOiJORmJaeHMyTE5uS3ZUVGlUTC9IaFlLUGJCVlBmMUdaeERKWUxIUXJ5RHJzPSIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoianE0eThEaFFpazJNUV9LUWhRTGx2QSIsInN1YiI6IjMzZGQ1YTBmLTJhMDgtNDViNS05YjFkLTIxZTc4ZjAzZDU4MiIsInBvdGE6ZW1haWwiOiJpazZsbWJAbGliZXJvLml0IiwicG90YTpncm91cHMiOiIiLCJjb2duaXRvOmdyb3VwcyI6WyJVcGxvYWQiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOi8vY29nbml0by1pZHAudXMtZWFzdC0yLmFtYXpvbmF3cy5jb20vdXMtZWFzdC0yX25BNWpaMGtsaCIsImNvZ25pdG86dXNlcm5hbWUiOiIzM2RkNWEwZi0yYTA4LTQ1YjUtOWIxZC0yMWU3OGYwM2Q1ODIiLCJhdWQiOiI3aGx1cWN0MG4ybmNraWI3aTdzZDU3NTNvYSIsImV2ZW50X2lkIjoiYTFkZGFkYjMtY2JkNC00Zjg1LWI2YjEtMzIwYzhkZGQyYTc0IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3ODM0MjQxOTIsInBvdGE6ZnVsbG5hbWUiOiJNYXNzaW1vIENhbXBhbmluaSIsInBvdGE6aWQiOiI2NjA4MSIsInBvdGE6Y2FsbHNpZ24iOiJJSzZMTUIiLCJleHAiOjE3ODM0Mjc3OTIsImlhdCI6MTc4MzQyNDE5MiwiZW1haWwiOiJpazZsbWJAbGliZXJvLml0In0.Tq38TVHTfP62CQe5LHf6_f-zpBDI8137G0y4VDaK4WsucnoqbBnyk2iDvTltvFGbGiLhFJLGwv6A2JwLHz4TJRm92dLVx5u9xNGJmg7KKds613H7ykJU4gewI2v7JCdP05XQquc50Wlkg82Uw9Sueu6XRtI_43BED_nERk0plC9zZgSmzJHhPUKsjx_FYNIVVAyMyTjK0RzrrQRPhr6pfjhHEMLA69PPVrwSgDkyYnmBH5jkxfvlJtONxJK_2WdRu7UvLUj-SmVJtyj8XNT27URXiKcy_ybTrupwK21YKD4Gj6nioUhU2eR7f9CSuddSTFbSa0sbaX_PzsyYeE2U3Q"

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
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            }
            
            response = await client.post(spot_url, json=pota_payload, headers=headers_spot)
            if response.status_code in [200, 201]:
                return {"success": True, "message": "Spot inviato!"}
            return {"success": False, "message": f"Errore server POTA: {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>File index.html non trovato</h1>")
