import json
import os
import urllib.request

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Fraction Calculator")

with open("index.html", "r") as f:
    INDEX_HTML = f.read()

# Tips go through North River Pay (the shared Square service). The app key stays server-side.
PAY_URL = (os.getenv("PAY_URL") or "").rstrip("/")
PAY_APP_ID = os.getenv("PAY_APP_ID") or "fraction-calc"
PAY_APP_KEY = os.getenv("PAY_APP_KEY") or ""
PUBLIC_URL = (os.getenv("PUBLIC_URL") or "https://fraction-calc-production.up.railway.app").rstrip("/")


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML


@app.get("/health")
def health():
    return {"status": "ok", "tips": bool(PAY_URL and PAY_APP_KEY)}


@app.post("/tip")
async def tip(request: Request):
    try:
        cents = int((await request.json()).get("cents") or 0)
    except Exception:
        cents = 0
    if not 100 <= cents <= 50000:
        return JSONResponse({"error": "Tips can be $1 to $500."}, status_code=400)
    if not (PAY_URL and PAY_APP_KEY):
        return JSONResponse({"error": "Tips aren't set up yet."}, status_code=503)
    body = json.dumps({"user_ref": "tip", "cents": cents, "redirect_url": f"{PUBLIC_URL}/?tipped=1",
                       "label": f"Tip for Fraction Calculator ${cents / 100:.2f}"}).encode()
    req = urllib.request.Request(f"{PAY_URL}/v1/checkout", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "X-App-Id": PAY_APP_ID,
                                          "X-App-Key": PAY_APP_KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read() or b"{}").get("error")
        except Exception:
            msg = None
        return JSONResponse({"error": msg or "Checkout unavailable, try again."}, status_code=502)
    except Exception:
        return JSONResponse({"error": "Checkout unavailable, try again."}, status_code=502)
    return {"url": data.get("url")}
