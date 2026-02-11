from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json
import os
from app.core.github_service import full_bulk_pr_workflow

router = APIRouter()

# Simple persistent storage for demo purposes
STORAGE_PATH = "/tmp/optimizer_consent.json"

def load_consent_data():
    if os.path.exists(STORAGE_PATH):
        try:
            with open(STORAGE_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_consent_data(data):
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f)

class ConsentRegisterRequest(BaseModel):
    url: str
    path: str
    original_content: str
    optimized_content: str
    pr_title: Optional[str] = "✨ [Optimizer] Better Dockerfile"
    commit_message: Optional[str] = "chore: optimize Dockerfile via Optimizer"

@router.post("/consent/register")
def register_consent(request: ConsentRegisterRequest):
    consent_id = str(uuid.uuid4())
    data = load_consent_data()
    data[consent_id] = request.dict()
    save_consent_data(data)
    return {"consent_id": consent_id}

@router.get("/consent/{consent_id}")
def get_consent(consent_id: str):
    data = load_consent_data()
    if consent_id not in data:
        raise HTTPException(status_code=404, detail="Consent request not found")
    return data[consent_id]

@router.post("/consent/{consent_id}/approve")
def approve_consent(consent_id: str):
    data = load_consent_data()
    if consent_id not in data:
        raise HTTPException(status_code=404, detail="Consent request not found")
    
    item = data[consent_id]
    
    # Trigger the PR flow using the service bot (no token passed)
    try:
        from app.core.github_service import extract_repo_info
        owner, repo, _ = extract_repo_info(item["url"])
        
        pr_link = full_bulk_pr_workflow(
            owner=owner,
            repo=repo,
            updates=[{"path": item["path"], "content": item["optimized_content"]}],
            pr_title=item["pr_title"],
            commit_message=item["commit_message"]
        )
        
        # Clean up storage after approval
        # del data[consent_id]
        # save_consent_data(data)
        
        return {"pr_link": pr_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
