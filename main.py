import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Document, Edit

app = FastAPI(title="Writing Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Writing Assistant Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Simple in-API rewriter that transforms text without attempting to evade detectors
class RewriteRequest(BaseModel):
    text: str
    mode: str = "clarity"  # clarity | concise | formal | expand | summarize | bulletize

class RewriteResponse(BaseModel):
    original: str
    rewritten: str
    mode: str


def rewrite_text(text: str, mode: str) -> str:
    # Lightweight, deterministic transformations (no external AI calls)
    cleaned = text.strip()
    if mode == "concise":
        # Compress multiple spaces and remove filler words lightly
        import re
        s = re.sub(r"\s+", " ", cleaned)
        fillers = ["basically", "actually", "really", "very", "just"]
        tokens = [t for t in s.split(" ") if t.lower() not in fillers]
        return " ".join(tokens)
    if mode == "formal":
        replacements = {
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "I'm": "I am",
            "it's": "it is",
            "gonna": "going to",
            "kinda": "somewhat",
            "sort of": "somewhat",
        }
        out = cleaned
        for k, v in replacements.items():
            out = out.replace(k, v).replace(k.capitalize(), v)
        return out
    if mode == "expand":
        return cleaned + "\n\nIn other words, this section is elaborated to provide additional context and smoother transitions between ideas."
    if mode == "summarize":
        # Naive summary: first sentence
        period = cleaned.find('.')
        return cleaned if period == -1 else cleaned[:period+1]
    if mode == "bulletize":
        lines = [l.strip("- •\t ") for l in cleaned.split('\n') if l.strip()]
        if len(lines) == 1:
            parts = [p.strip() for p in cleaned.replace(';', ',').split(',') if p.strip()]
            lines = parts
        return "\n".join(f"• {l}" for l in lines)
    # default clarity: trim and normalize spacing
    return " ".join(cleaned.split())

@app.post("/api/rewrite", response_model=RewriteResponse)
def api_rewrite(req: RewriteRequest):
    rewritten = rewrite_text(req.text, req.mode)
    return RewriteResponse(original=req.text, rewritten=rewritten, mode=req.mode)

# Minimal persistence endpoints for documents and edits
@app.post("/api/documents", response_model=dict)
def create_document_api(doc: Document):
    try:
        inserted_id = create_document("document", doc)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=List[dict])
def list_documents_api(limit: int = 20):
    try:
        docs = get_documents("document", limit=limit)
        # Convert ObjectId to str
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/edits", response_model=dict)
def create_edit_api(edit: Edit):
    try:
        inserted_id = create_document("edit", edit)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
