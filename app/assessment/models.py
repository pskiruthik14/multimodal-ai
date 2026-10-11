"""
Data models for Adaptive Assessment & Question Verification
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class QuestionType(str, Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    NUMERICAL = "numerical"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question(BaseModel):
    id: str
    topic_id: str
    topic_name: str
    type: QuestionType
    difficulty: DifficultyLevel
    irt_difficulty_b: float = 0.0  # Item Response Theory item difficulty parameter
    irt_discrimination_a: float = 1.0 # Item discrimination parameter
    question_text: str
    options: List[str] = Field(default_factory=list) # Options A, B, C, D for MCQ
    correct_answer: str
    solution_explanation: str
    misconception_distractors: Dict[str, str] = Field(default_factory=dict) # Option -> Misconception explanation
    citation_label: str
    source_unit_id: str
    verification_status: str = "verified_cross_model"
    tolerance: Optional[float] = None # For numerical questions

class QuizSubmission(BaseModel):
    student_id: str = "student_default"
    answers: Dict[str, str] # question_id -> student answer
    time_spent_seconds: Optional[int] = None

class QuestionResult(BaseModel):
    question_id: str
    question_text: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    citation_label: str
    solution_explanation: str
    misconception_diagnosed: Optional[str] = None
    topic_id: str
    topic_name: str

class DiagnosticReport(BaseModel):
    student_id: str
    score: int
    total_questions: int
    accuracy_percentage: float
    results: List[QuestionResult]
    topic_breakdown: Dict[str, Dict[str, Any]]
    identified_misconceptions: List[Dict[str, str]]
    recommended_review_units: List[Dict[str, Any]]
    bkt_mastery_updates: Dict[str, float]
    estimated_ability_theta: float
