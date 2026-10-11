"""
Configuration settings for the Multimodal AI Study Companion
Track D: Personalized Tutoring & Adaptive Learning
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
STATIC_DIR = BASE_DIR / "app" / "static"

class Settings(BaseSettings):
    APP_NAME: str = "SynapseLearn AI: Multimodal Study Companion"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # API Keys (Supports Gemini / Google AI API or offline mock fallback)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Bayesian Knowledge Tracing (BKT) Default Hyperparameters
    BKT_PRIOR: float = 0.20        # P(L0): Initial probability student knows concept
    BKT_TRANSITION: float = 0.15   # P(T): Probability of learning concept between steps
    BKT_GUESS: float = 0.20        # P(G): Probability of guessing correctly without mastery
    BKT_SLIP: float = 0.10         # P(S): Probability of making a mistake despite mastery
    BKT_MASTERY_THRESHOLD: float = 0.85 # Threshold to declare topic mastered
    
    # Item Response Theory (IRT)
    IRT_DEFAULT_ABILITY: float = 0.0 # Theta baseline
    
    # Spaced Repetition (Ebbinghaus)
    FORGETTING_RATE: float = 0.35 # Decay factor in R = exp(-t / (S * factor))
    
    # Grounding & Guardrail Thresholds
    GROUNDING_SIMILARITY_THRESHOLD: float = 0.25 # Below this -> out-of-scope refusal
    HIGH_CONFIDENCE_THRESHOLD: float = 0.55
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    STATIC_DIR: Path = STATIC_DIR

settings = Settings()
