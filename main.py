import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI(title="Fraction Calculator")
security = HTTPBasic()

AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "changeme")

with open("index.html", "r") as f:
    INDEX_HTML = f.read()

def verify(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username.strip().lower(), AUTH_USER.strip().lower())
    correct_pass = secrets.compare_digest(credentials.password, AUTH_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/", response_class=HTMLResponse)
def home(user: str = Depends(verify)):
    return INDEX_HTML

@app.get("/health")
def health():
    return {"status": "ok"}
