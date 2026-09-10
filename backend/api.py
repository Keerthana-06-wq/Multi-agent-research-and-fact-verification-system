from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.core.models import (
    VerificationRequest,
    VerificationResponse,
    SourceItem
)
from backend.core.orchestrator import MultiAgentOrchestrator

app = FastAPI(
    title="Veritas | Advanced Fact Verification Agent",
    description="18-step verification pipeline operating on 'Verify First, Answer Second'.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = MultiAgentOrchestrator()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

PRESET_DEMO_CASES = [
    {
        "id": 1,
        "label": "India independent 1947 (strip 'true')",
        "category": "Historical",
        "query": "India became independent in 1947 true",
        "expected_verdict": "TRUE",
        "description": "Step 1: Ignores user suggested 'true' answer and verifies historical fact."
    },
    {
        "id": 2,
        "label": "2 + 2 = 5 (strip 'false')",
        "category": "Mathematical",
        "query": "2 + 2 = 5 false",
        "expected_verdict": "FALSE",
        "description": "Step 1 & 4: Ignores user suggested 'false' answer and calculates 4 != 5."
    },
    {
        "id": 3,
        "label": "Water does not contain oxygen",
        "category": "Scientific (Negation)",
        "query": "Water does not contain oxygen.",
        "expected_verdict": "FALSE",
        "description": "Step 2 & 9: Underlying proposition (water contains oxygen) is true, so negative claim is FALSE."
    },
    {
        "id": 4,
        "label": "The Sun does not rise in the west",
        "category": "Scientific (Negation)",
        "query": "The Sun does not rise in the west.",
        "expected_verdict": "TRUE",
        "description": "Step 2 & 9: Sun rises in east (west is false), so negative claim is TRUE."
    },
    {
        "id": 5,
        "label": "India is not in Europe",
        "category": "Geographical (Negation)",
        "query": "India is not in Europe.",
        "expected_verdict": "TRUE",
        "description": "Step 2 & 6: India is in Asia (not Europe), so negative statement is TRUE."
    },
    {
        "id": 6,
        "label": "India is not in Asia",
        "category": "Geographical (Negation)",
        "query": "India is not in Asia.",
        "expected_verdict": "FALSE",
        "description": "Step 2 & 6: India is in Asia, so claiming it is not in Asia is FALSE."
    },
    {
        "id": 7,
        "label": "Humans cannot breathe underwater",
        "category": "Real-life",
        "query": "Humans cannot breathe underwater without equipment.",
        "expected_verdict": "TRUE",
        "description": "Step 8: Human biological reality requires diving equipment to breathe underwater."
    },
    {
        "id": 8,
        "label": "All birds can fly",
        "category": "Universal Quantifier",
        "query": "All birds can fly.",
        "expected_verdict": "FALSE",
        "description": "Step 10: 'ALL' makes claim strict; flightless birds (penguins, ostriches) make it FALSE."
    },
    {
        "id": 9,
        "label": "Pacific Ocean larger than Atlantic",
        "category": "Comparison",
        "query": "The Pacific Ocean is larger than the Atlantic Ocean.",
        "expected_verdict": "TRUE",
        "description": "Step 11: Compares oceanic surface areas (165M km² vs 106M km²)."
    },
    {
        "id": 10,
        "label": "Atlantic Ocean larger than Pacific",
        "category": "Comparison",
        "query": "The Atlantic Ocean is larger than the Pacific Ocean.",
        "expected_verdict": "FALSE",
        "description": "Step 11: Verified comparison contradiction."
    },
    {
        "id": 11,
        "label": "India 1947 AND Mumbai capital",
        "category": "Multiple Claims",
        "query": "India became independent in 1947 and Mumbai is the capital of India.",
        "expected_verdict": "FALSE",
        "description": "Step 12: Separates claims: Claim 1 is TRUE, Claim 2 is FALSE -> Overall FALSE."
    },
    {
        "id": 12,
        "label": "Fish do not live on land",
        "category": "Real-life (Negation)",
        "query": "Fish do not live on land.",
        "expected_verdict": "TRUE",
        "description": "Step 9: Proposition 'Fish live on land' is false -> Negative statement is TRUE."
    },
    {
        "id": 13,
        "label": "Freezing water will not turn to ice",
        "category": "Physical Law",
        "query": "freezing of water will not turns into ice",
        "expected_verdict": "FALSE",
        "description": "Thermodynamic phase change contradiction."
    }
]

@app.get("/health")
def health_check():
    return {"status": "ok", "system": "Veritas 18-Step Advanced Fact Verification Agent"}

@app.get("/api/preset-cases")
def get_preset_cases():
    return PRESET_DEMO_CASES

@app.post("/api/verify", response_model=VerificationResponse)
def verify_claim(req: VerificationRequest):
    try:
        return orchestrator.process(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    @app.get("/index.html")
    def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")
