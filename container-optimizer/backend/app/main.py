from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import containers, auth
import requests

app = FastAPI(
    title="Docker Container Optimizer",
    description="Real-time Docker container optimization & security platform",
    version="0.1.0"
)

def get_headers(token: str):
    """Helper to get authorization headers."""
    return {"Authorization": f"token {token}"}

def get_authenticated_user(token: str) -> str:
    """Gets the login name of the authenticated user. Safe for CI."""
    try:
        url = "https://api.github.com/user"
        resp = requests.get(url, headers=get_headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()["login"]
    except Exception:
        pass
    
    # Standard GitHub Actions tokens don't have access to /user
    return "github-actions[bot]"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(containers.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.get("/")
def health():
    return {"status": "running", "version": "v11.3-stable"}
