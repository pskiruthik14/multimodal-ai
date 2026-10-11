"""
FastAPI Routes for SynapseLearn AI Study Companion
Track D: Personalized Tutoring & Adaptive Learning
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.ingestion.preloaded_course import get_preloaded_course
from app.ingestion.models import Course, ContentUnit, SourceType
from app.ingestion.extractor import MultimodalExtractor
from app.ingestion.topic_tagger import KnowledgeGraphManager
from app.grounding.retriever import HybridRetriever
from app.grounding.tutor import GroundedTutor
from app.assessment.generator import AdaptiveAssessmentGenerator
from app.assessment.diagnostic import AssessmentDiagnosticEngine
from app.assessment.models import QuizSubmission, DifficultyLevel
from app.learner_model.bkt import LearnerModel
from app.learner_model.forgetting_curve import ForgettingCurveTracker
from app.learner_model.diagnostic_intake import DiagnosticIntakeManager
from app.evaluation.eval_runner import SystemEvaluationRunner
from app.evaluation.student_simulator import MultiSessionSimulator
from app.evaluation.benchmark_dataset import BENCHMARK_TEST_SET
from app.revision.generator import RevisionSuiteManager
from app.grounding.ai_features import AIMisconceptionClinic, AIDiagramExplainer, AIConceptComparator
from app.services.ai_service import AIService
from app.config import settings

router = APIRouter(prefix="/api")

# Global singleton states
course: Course = get_preloaded_course()
retriever = HybridRetriever(course.content_units)
kg_manager = KnowledgeGraphManager(course)
learner_model = LearnerModel(student_id="student_default")
forgetting_tracker = ForgettingCurveTracker()
assessment_generator = AdaptiveAssessmentGenerator()
diagnostic_engine = AssessmentDiagnosticEngine(assessment_generator)
tutor = GroundedTutor(course, retriever, learner_model)

# ----------------- Models for Request Payloads -----------------
class ChatRequest(BaseModel):
    query: str
    bilingual_mode: bool = False
    persona: str = "professor" # professor, feynman, socratic, cram, hinglish
    api_key_override: Optional[str] = None

class GenerateQuizRequest(BaseModel):
    topic_ids: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None
    num_questions: int = 4

class AIGenerateQuizRequest(BaseModel):
    topic_id: str = "topic-1"
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    num_questions: int = 3
    api_key_override: Optional[str] = None

class RemediateRequest(BaseModel):
    misconception: str
    topic_name: str = "Deep Learning Foundations"
    api_key_override: Optional[str] = None

class DiagramExplainRequest(BaseModel):
    unit_id: str
    api_key_override: Optional[str] = None

class ComparisonRequest(BaseModel):
    comparison_key: str = "optimizers"
    api_key_override: Optional[str] = None

class AIFlashcardsRequest(BaseModel):
    topic_id: str = "topic-1"
    num_cards: int = 3
    api_key_override: Optional[str] = None

class AICheatSheetRequest(BaseModel):
    topic_id: str = "topic-1"
    api_key_override: Optional[str] = None

class AIAudioBriefRequest(BaseModel):
    topic_id: str = "topic-1"
    api_key_override: Optional[str] = None

class IntakeRequest(BaseModel):
    self_reported_level: str # "beginner", "intermediate", "advanced"
    diagnostic_score: int     # 0 to 3

class StudyScheduleRequest(BaseModel):
    days_until_exam: int = 7
    hours_per_day: float = 2.0
    api_key_override: Optional[str] = None

class SimulationRequest(BaseModel):
    profile_key: str = "intermediate"
    num_sessions: int = 5
    questions_per_session: int = 2

# ----------------- 1. Course & Knowledge Base -----------------
@router.get("/course")
def get_course_data():
    """Returns course structure, topics, and multimodal content units."""
    return {
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "description": course.description,
        "topics": [t.model_dump() for t in course.topics],
        "content_units": [u.model_dump() for u in course.content_units],
        "total_units": len(course.content_units)
    }

@router.get("/units/{unit_id}")
def get_unit_details(unit_id: str):
    """Returns details and citation modal data for a single content unit."""
    unit = next((u for u in course.content_units if u.id == unit_id), None)
    if not unit:
        raise HTTPException(status_code=404, detail="Content unit not found")
    return tutor.citation_engine.build_citation_modal_data(unit)

@router.post("/upload")
async def upload_material(file: UploadFile = File(...)):
    """Uploads and ingests a textbook (.pdf), slides (.pptx), or video transcript (.vtt/.srt/.txt)."""
    filename = file.filename
    ext = Path(filename).suffix.lower()
    
    save_path = settings.UPLOADS_DIR / filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_units: List[ContentUnit] = []
    if ext == ".pdf":
        extracted_units = MultimodalExtractor.extract_from_pdf(save_path, filename)
    elif ext in [".pptx", ".ppt"]:
        extracted_units = MultimodalExtractor.extract_from_pptx(save_path, filename)
    elif ext in [".vtt", ".srt", ".txt", ".json"]:
        extracted_units = MultimodalExtractor.extract_from_transcript(save_path, filename)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    # Tag extracted units, enrich with AI, and add to course
    for u in extracted_units:
        kg_manager.tag_content_unit(u)
        if not u.equations or not u.visual_description:
            try:
                enrichment = await AIService.enrich_uploaded_content(u.text_content, filename)
                if enrichment and isinstance(enrichment, dict):
                    if not u.equations and enrichment.get("equations"):
                        u.equations = enrichment["equations"]
                    if not u.visual_description and enrichment.get("visual_description"):
                        u.visual_description = enrichment["visual_description"]
            except Exception:
                pass
        course.content_units.append(u)

    # Re-index hybrid retriever
    global retriever, tutor
    retriever = HybridRetriever(course.content_units)
    tutor = GroundedTutor(course, retriever, learner_model)

    return {
        "status": "success",
        "filename": filename,
        "units_extracted": len(extracted_units),
        "total_course_units": len(course.content_units)
    }

@router.post("/ingestion/load-dummy-data")
def load_dummy_data():
    """Ingests sample dummy materials (VTT transcripts, SRT subtitles, and Textbook notes) into the course."""
    dummy_dir = settings.DATA_DIR / "dummy_datasets"
    loaded_files = []
    total_new_units = 0

    vtt_file = dummy_dir / "lecture_transformers_attention.vtt"
    if vtt_file.exists():
        units = MultimodalExtractor.extract_from_transcript(vtt_file, "lecture_transformers_attention.vtt")
        for u in units:
            kg_manager.tag_content_unit(u)
            course.content_units.append(u)
        total_new_units += len(units)
        loaded_files.append("lecture_transformers_attention.vtt")

    srt_file = dummy_dir / "lecture_convnet_architectures.srt"
    if srt_file.exists():
        units = MultimodalExtractor.extract_from_transcript(srt_file, "lecture_convnet_architectures.srt")
        for u in units:
            kg_manager.tag_content_unit(u)
            course.content_units.append(u)
        total_new_units += len(units)
        loaded_files.append("lecture_convnet_architectures.srt")

    txt_file = dummy_dir / "textbook_optimization_curvature.txt"
    if txt_file.exists():
        units = MultimodalExtractor.extract_from_transcript(txt_file, "textbook_optimization_curvature.txt")
        for u in units:
            kg_manager.tag_content_unit(u)
            course.content_units.append(u)
        total_new_units += len(units)
        loaded_files.append("textbook_optimization_curvature.txt")

    # Re-index hybrid retriever
    global retriever, tutor
    retriever = HybridRetriever(course.content_units)
    tutor = GroundedTutor(course, retriever, learner_model)

    return {
        "status": "success",
        "loaded_files": loaded_files,
        "new_units_added": total_new_units,
        "total_course_units": len(course.content_units)
    }

@router.get("/knowledge-graph")
def get_knowledge_graph():
    """Returns nodes and edges for the Course Flow Map with live student mastery colors."""
    mastery_map = learner_model.get_all_mastery()
    return kg_manager.get_graph_export(mastery_map)

# ----------------- 2. Tutor Chat & Grounding -----------------
@router.post("/chat")
async def chat_with_tutor(req: ChatRequest):
    """Processes student query with hybrid retrieval, grounding verification, and citations."""
    response = await tutor.answer_query(
        query=req.query,
        bilingual_mode=req.bilingual_mode,
        persona=req.persona,
        api_key_override=req.api_key_override
    )
    return response

# ----------------- 3. Adaptive Assessment & AI Generator -----------------
@router.post("/assessment/generate")
def generate_assessment(req: GenerateQuizRequest):
    """Generates customized quiz matching scope, verified for correctness and deduplicated."""
    questions = assessment_generator.generate_quiz(
        student_id=learner_model.student_id,
        topic_ids=req.topic_ids,
        difficulty=req.difficulty,
        num_questions=req.num_questions
    )
    return {
        "quiz_id": f"quiz-{len(learner_model.topic_states) + 1}",
        "questions": [q.model_dump() for q in questions],
        "total_questions": len(questions)
    }

@router.post("/assessment/ai-generate")
async def generate_ai_assessment(req: AIGenerateQuizRequest):
    """Dynamically synthesizes novel, verified questions using AI matching topic and difficulty."""
    questions = await assessment_generator.generate_ai_questions(
        student_id=learner_model.student_id,
        topic_id=req.topic_id,
        difficulty=req.difficulty,
        num_questions=req.num_questions,
        api_key_override=req.api_key_override
    )
    return {
        "quiz_id": f"ai-quiz-{len(learner_model.topic_states) + 1}",
        "questions": [q.model_dump() for q in questions],
        "total_questions": len(questions)
    }

@router.post("/assessment/submit")
def submit_assessment(submission: QuizSubmission):
    """Evaluates quiz, diagnoses misconceptions, gives cited feedback, and updates BKT/IRT."""
    results, stats = diagnostic_engine.evaluate_quiz(submission)
    
    # Update BKT and IRT
    total_score = sum(1 for r in results if r.is_correct)
    responses_for_irt = []
    
    for r in results:
        learner_model.record_quiz_answer(r.topic_id, r.topic_name, r.is_correct)
        q_obj = assessment_generator.get_question_by_id(r.question_id)
        if q_obj:
            responses_for_irt.append((r.is_correct, q_obj.irt_discrimination_a, q_obj.irt_difficulty_b))

    # Update IRT ability
    from app.learner_model.irt import IRTEngine
    learner_model.ability_theta = IRTEngine.estimate_ability_eap(responses_for_irt)
    learner_model.quizzes_taken += 1

    # Reset forgetting curve for topics tested successfully
    for t_id, t_stat in stats["topic_stats"].items():
        forgetting_tracker.record_review(t_id, success=(t_stat["accuracy"] >= 0.50))

    # Find recommended review units for weak topics (< 60% score)
    weak_topic_ids = [t_id for t_id, data in stats["topic_stats"].items() if data["accuracy"] < 0.60]
    recommended_units = [
        u.model_dump() for u in course.content_units if u.topic_id in weak_topic_ids
    ][:3]

    return {
        "student_id": submission.student_id,
        "score": total_score,
        "total_questions": len(results),
        "accuracy_percentage": round((total_score / max(1, len(results))) * 100, 1),
        "results": [r.model_dump() for r in results],
        "topic_breakdown": stats["topic_stats"],
        "identified_misconceptions": stats["misconceptions"],
        "recommended_review_units": recommended_units,
        "updated_bkt_mastery": learner_model.get_all_mastery(),
        "estimated_ability_theta": learner_model.ability_theta
    }

# ----------------- 4. Learner Model & Analytics -----------------
@router.get("/learner/mastery")
def get_learner_mastery():
    """Returns student BKT mastery summary, history, and IRT theta."""
    summary = learner_model.get_mastery_summary()
    # Add detailed topic states
    topic_details = {}
    for tid, state in learner_model.topic_states.items():
        topic_details[tid] = {
            "topic_id": tid,
            "topic_name": state.topic_name,
            "p_mastery": round(state.p_mastery, 3),
            "history": state.history
        }
    summary["topic_details"] = topic_details
    return summary

@router.get("/learner/forgetting-curve")
def get_forgetting_curve_data():
    """Returns memory retention percentages and spaced repetition schedule."""
    return {
        "schedule": forgetting_tracker.get_revision_schedule()
    }

@router.get("/learner/diagnostic-questions")
def get_diagnostic_screener():
    """Returns 3-question intake screener for zero-history onboarding."""
    return [q.model_dump() for q in DiagnosticIntakeManager.get_diagnostic_questions()]

@router.post("/learner/intake")
def complete_intake(req: IntakeRequest):
    """Calibrates baseline student prior and IRT ability from zero history."""
    global learner_model, tutor
    topic_ids = [t.id for t in course.topics]
    learner_model = DiagnosticIntakeManager.calibrate_new_student(
        student_id="student_default",
        self_reported_level=req.self_reported_level,
        diagnostic_score=req.diagnostic_score,
        course_topic_ids=topic_ids
    )
    tutor = GroundedTutor(course, retriever, learner_model)
    return {
        "status": "calibrated",
        "ability_theta": learner_model.ability_theta,
        "initial_mastery": learner_model.get_all_mastery()
    }

@router.post("/learner/reset")
def reset_student_model():
    """Resets student history to initial default baseline."""
    global learner_model, tutor
    learner_model = LearnerModel(student_id="student_default")
    tutor = GroundedTutor(course, retriever, learner_model)
    return {"status": "reset", "mastery": learner_model.get_all_mastery()}

# ----------------- 5. System Evaluation & Benchmarking -----------------
@router.get("/evaluation/benchmark-dataset")
def get_benchmark_dataset():
    """Returns curated benchmark queries (in-scope + adversarial out-of-scope)."""
    return [q.model_dump() for q in BENCHMARK_TEST_SET]

@router.post("/evaluation/run-benchmark")
def run_system_benchmark():
    """Executes live RAGAS evaluation runner and returns framework metrics."""
    eval_runner = SystemEvaluationRunner(retriever)
    results = eval_runner.run_benchmark()
    return results

@router.post("/evaluation/simulate-students")
def simulate_students(req: SimulationRequest):
    """Simulates multi-session longitudinal student runs, reporting mastery gains and 0% repetition."""
    topic_ids = [t.id for t in course.topics]
    sim = MultiSessionSimulator(topic_ids)
    results = sim.run_simulation(
        profile_key=req.profile_key,
        num_sessions=req.num_sessions,
        questions_per_session=req.questions_per_session
    )
    return results

# ----------------- 6. Smart Revision Suite -----------------
@router.get("/revision/flashcards")
def get_flashcards(topic_id: Optional[str] = None):
    """Returns Leitner 5-box spaced repetition flashcards."""
    return RevisionSuiteManager.get_flashcards(topic_id)

@router.get("/revision/cheat-sheet/{topic_id}")
def get_cheat_sheet(topic_id: str):
    """Returns targeted cheat sheet formulas and pitfalls for a weak topic."""
    sheet = RevisionSuiteManager.get_cheat_sheet(topic_id)
    if not sheet:
        raise HTTPException(status_code=404, detail="Cheat sheet not found for topic")
    return sheet

@router.post("/revision/study-schedule")
async def generate_study_schedule(req: StudyScheduleRequest):
    """Generates day-by-day exam prep schedule based on weak topics and forgetting curves using AI."""
    mastery_map = learner_model.get_all_mastery()
    weak_topic_ids = [tid for tid, m in mastery_map.items() if m < 0.60]
    return await RevisionSuiteManager.generate_ai_study_schedule(
        weak_topic_ids=weak_topic_ids,
        days_until_exam=req.days_until_exam,
        hours_per_day=req.hours_per_day,
        api_key_override=req.api_key_override
    )

@router.get("/revision/audio-brief/{topic_id}")
def get_audio_brief(topic_id: str):
    """Returns 2-minute audio brief summary script for speech synthesis."""
    return RevisionSuiteManager.generate_audio_brief(topic_id)

@router.post("/revision/ai-audio-brief")
async def generate_ai_audio_brief(req: AIAudioBriefRequest):
    """Dynamically generates 2-minute spoken conversational audio brief script using Generative AI."""
    return await RevisionSuiteManager.generate_ai_audio_brief(
        topic_id=req.topic_id,
        api_key_override=req.api_key_override
    )

@router.post("/revision/ai-cheat-sheet")
async def generate_ai_cheat_sheet(req: AICheatSheetRequest):
    """Dynamically generates high-yield exam cheat-sheet formulas and insights using Generative AI."""
    return await RevisionSuiteManager.generate_ai_cheat_sheet(
        topic_id=req.topic_id,
        api_key_override=req.api_key_override
    )

@router.post("/revision/ai-flashcards")
async def generate_ai_flashcards(req: AIFlashcardsRequest):
    """Dynamically synthesizes novel Leitner flashcards using Generative AI/Gemini."""
    return await RevisionSuiteManager.generate_ai_flashcards(
        topic_id=req.topic_id,
        num_cards=req.num_cards,
        api_key_override=req.api_key_override
    )

# ----------------- 7. Advanced Multimodal AI Features -----------------
@router.post("/ai/remediate")
async def remediate_misconception(req: RemediateRequest):
    """Generates targeted cognitive diagnostic breakdown and interactive follow-up challenge for misconceptions."""
    return await AIMisconceptionClinic.remediate(
        misconception_text=req.misconception,
        topic_name=req.topic_name,
        api_key_override=req.api_key_override
    )

@router.post("/ai/diagram-explain")
async def explain_diagram(req: DiagramExplainRequest):
    """Provides deep structural diagram analysis and vector flow breakdowns for figures dynamically via AI."""
    unit = next((u for u in course.content_units if u.id == req.unit_id), None)
    return await AIDiagramExplainer.explain_diagram_ai(
        unit_id=req.unit_id,
        content_unit=unit,
        api_key_override=req.api_key_override
    )

@router.post("/ai/compare")
async def compare_concepts(req: ComparisonRequest):
    """Generates comprehensive trade-off comparison matrices for ANY concepts dynamically via Generative AI."""
    return await AIConceptComparator.compare_concepts_ai(
        comparison_key=req.comparison_key,
        api_key_override=req.api_key_override
    )

@router.get("/ai/status")
def get_ai_status():
    """Returns AI Engine model configuration, active capabilities, and health status."""
    return {
        "status": "online",
        "model": settings.GEMINI_MODEL,
        "api_key_configured": bool(settings.GEMINI_API_KEY),
        "engine": "Google Gemini 2.0 / 2.5 Flash + Multimodal Generative Synthesis",
        "capabilities": [
            "Source-Grounded Multimodal Tutor",
            "Multi-Persona Synthesis (Professor, Feynman, Socratic, Cram, Hinglish)",
            "Dynamic AI Question Synthesis with Misconception Distractors",
            "Cognitive Misconception Remediation Clinic",
            "Generative Concept & Trade-off Matrix Comparator",
            "Multimodal Neural Architecture & Diagram Explainer",
            "Dynamic Leitner Spaced-Repetition Flashcards",
            "Generative High-Yield Exam Cheat-Sheets",
            "Spoken 2-Minute Audio Brief Script Synthesis",
            "Adaptive Spaced-Repetition Study Timetable",
            "Multimodal Document Ingestion & Formula Enrichment"
        ]
    }

