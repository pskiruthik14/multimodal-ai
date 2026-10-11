"""
SynapseLearn AI: Multimodal Study Companion
Track D: Personalized Tutoring & Adaptive Learning
Hackathon 2026 Entrypoint
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.api.routes import router as api_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multimodal source-grounded study companion with Bayesian Knowledge Tracing and Adaptive Assessments."
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount Static Files
static_dir = Path(__file__).resolve().parent / "app" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    """Serves the main single-page web app."""
    return FileResponse(static_dir / "index.html")

@app.on_event("startup")
def on_startup():
    print("=" * 60)
    print(">> SynapseLearn AI: Multimodal Study Companion Started!")
    print(">> Loaded Course: CS229: Deep Learning & Neural Architectures")
    print(">> Server Running at: http://127.0.0.1:8080")
    print("=" * 60)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))
    print(f">> Starting SynapseLearn AI on port {port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
