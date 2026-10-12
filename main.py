from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Fraction Calculator")

with open("index.html", "r") as f:
    INDEX_HTML = f.read()

@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML

@app.get("/health")
def health():
    return {"status": "ok"}
