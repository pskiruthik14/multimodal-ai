"""
Comprehensive Automated Test Suite for SynapseLearn AI
Verifies Knowledge Base Ingestion, Grounding, Refusal, BKT, Assessment, and Evaluation.
"""

import pytest
from app.ingestion.preloaded_course import get_preloaded_course
from app.ingestion.topic_tagger import KnowledgeGraphManager
from app.grounding.retriever import HybridRetriever
from app.grounding.verifier import GroundingVerifier
from app.assessment.generator import AdaptiveAssessmentGenerator
from app.assessment.diagnostic import AssessmentDiagnosticEngine
from app.assessment.models import QuizSubmission, QuestionType
from app.learner_model.bkt import LearnerModel
from app.learner_model.irt import IRTEngine
from app.learner_model.diagnostic_intake import DiagnosticIntakeManager
from app.evaluation.eval_runner import SystemEvaluationRunner
from app.evaluation.student_simulator import MultiSessionSimulator
from app.evaluation.benchmark_dataset import BENCHMARK_TEST_SET

def test_course_ingestion_and_graph():
    course = get_preloaded_course()
    assert len(course.topics) == 6
    assert len(course.content_units) >= 10
    
    kg = KnowledgeGraphManager(course)
    path = kg.get_learning_path()
    assert len(path) == 6
    assert path[0] == "topic-1" # Prerequisite must precede advanced
    
    export = kg.get_graph_export()
    assert len(export["nodes"]) == 6
    assert len(export["edges"]) >= 5

def test_grounding_retrieval_and_refusal():
    course = get_preloaded_course()
    retriever = HybridRetriever(course.content_units)
    
    # 1. In-scope query
    results = retriever.retrieve("Why does Adam use bias correction?", top_k=2)
    assert len(results) > 0
    top_unit, score = results[0]
    assert "Adam" in top_unit.title or "topic-2" in top_unit.topic_id
    
    verif = GroundingVerifier.check_query_grounding("Why does Adam use bias correction?", results)
    assert verif["is_grounded"] is True
    
    # 2. Adversarial out-of-scope query
    adv_query = "What is the traditional recipe to bake a chocolate lava cake?"
    adv_results = retriever.retrieve(adv_query, top_k=2)
    adv_verif = GroundingVerifier.check_query_grounding(adv_query, adv_results)
    assert adv_verif["is_grounded"] is False
    assert "DECLINED" in adv_verif["status"]

def test_bkt_learner_model():
    model = LearnerModel("test_student")
    state = model.get_or_create_topic_state("topic-1", "Loss Functions", prior=0.20)
    
    # Test correct observation increases mastery
    new_m = state.update(is_correct=True)
    assert new_m > 0.20
    
    # Test consecutive correct answers leads to high mastery
    for _ in range(4):
        state.update(is_correct=True)
    assert state.p_mastery >= 0.70

def test_irt_ability_estimation():
    responses = [
        (True, 1.2, 0.0),
        (True, 1.4, 0.5),
        (False, 1.5, 1.2)
    ]
    theta = IRTEngine.estimate_ability_eap(responses)
    assert -1.5 <= theta <= 2.0

def test_adaptive_assessment_and_diagnostic():
    generator = AdaptiveAssessmentGenerator()
    questions = generator.generate_quiz("test_student", num_questions=2)
    assert len(questions) == 2
    
    # Simulate quiz submission
    submission = QuizSubmission(
        student_id="test_student",
        answers={
            questions[0].id: questions[0].correct_answer, # Correct
            questions[1].id: "Z" if questions[1].type == QuestionType.MCQ else "999" # Wrong
        }
    )
    
    diag_engine = AssessmentDiagnosticEngine(generator)
    results, stats = diag_engine.evaluate_quiz(submission)
    assert len(results) == 2
    assert results[0].is_correct is True
    assert results[1].is_correct is False

def test_evaluation_runner_and_student_simulator():
    course = get_preloaded_course()
    retriever = HybridRetriever(course.content_units)
    eval_runner = SystemEvaluationRunner(retriever)
    
    benchmark_report = eval_runner.run_benchmark()
    metrics = benchmark_report["summary_metrics"]
    
    assert metrics["faithfulness"] >= 0.85
    assert metrics["hallucination_refusal_rate"] == 1.0 # Strict refusal for all 4 adversarial queries
    assert metrics["overall_score"] >= 0.80
    
    # Test multi-session simulation
    sim = MultiSessionSimulator([t.id for t in course.topics])
    sim_res = sim.run_simulation(profile_key="intermediate", num_sessions=3, questions_per_session=2)
    assert sim_res["net_mastery_gain"] > 0
    assert sim_res["question_repetition_rate"] == 0.0 # Zero repetition across sessions

def test_ai_features_and_personas():
    import asyncio
    from app.grounding.tutor import GroundedTutor
    from app.grounding.ai_features import AIMisconceptionClinic, AIDiagramExplainer, AIConceptComparator
    from app.revision.generator import RevisionSuiteManager
    
    course = get_preloaded_course()
    retriever = HybridRetriever(course.content_units)
    learner = LearnerModel("ai_test_student")
    tutor = GroundedTutor(course, retriever, learner)
    
    # 1. Test Personas
    loop = asyncio.new_event_loop()
    feynman_res = loop.run_until_complete(tutor.answer_query("How does Adam optimizer work?", persona="feynman"))
    assert "Feynman" in feynman_res["answer"] or "Analogy" in feynman_res["answer"]
    assert feynman_res["is_grounded"] is True
    
    socratic_res = loop.run_until_complete(tutor.answer_query("Explain ResNet skip connection", persona="socratic"))
    assert "Socratic" in socratic_res["answer"] or "Inquiry" in socratic_res["answer"]
    
    cram_res = loop.run_until_complete(tutor.answer_query("Explain Cross-Entropy Loss", persona="cram"))
    assert "Exam Cram" in cram_res["answer"] or "Formula" in cram_res["answer"]
    
    # 2. Test AI Dynamic Question Generation
    generator = AdaptiveAssessmentGenerator()
    ai_questions = loop.run_until_complete(generator.generate_ai_questions("ai_test_student", "topic-1", num_questions=2))
    assert len(ai_questions) >= 1
    assert ai_questions[0].topic_id == "topic-1"
    assert ai_questions[0].verification_status == "verified_cross_model"
    
    # 3. Test AI Misconception Clinic
    rem = loop.run_until_complete(AIMisconceptionClinic.remediate("Memory misconception: Cross-entropy uses less RAM", "Loss Functions"))
    assert "Memory" in rem["title"] or "Remediation" in rem["title"]
    assert len(rem["practice_check"]["options"]) >= 2
    
    # 4. Test Diagram Explainer & Comparator
    diag = AIDiagramExplainer.explain_diagram("unit-tb-01")
    assert "Quadratic Bowl" in diag["title"]
    assert len(diag["visual_elements"]) >= 3
    
    comp = AIConceptComparator.get_comparison("optimizers")
    assert len(comp["rows"]) == 4
    
    # 5. Test AI Flashcards
    fc = loop.run_until_complete(RevisionSuiteManager.generate_ai_flashcards("topic-2", num_cards=2))
    assert len(fc) == 2
    assert "Adam" in fc[0]["front"] or "Optimizer" in fc[0]["front"] or "Formula" in fc[0]["back"]
    loop.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])

