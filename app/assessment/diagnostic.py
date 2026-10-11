"""
Diagnostic Assessment Engine:
Evaluates student quiz submissions, diagnoses misconceptions,
generates cited step-by-step corrective feedback, and identifies weak topics.
"""

from typing import List, Dict, Any, Tuple
import re
from app.assessment.models import (
    QuizSubmission, DiagnosticReport, QuestionResult, Question, QuestionType
)
from app.assessment.generator import AdaptiveAssessmentGenerator

class AssessmentDiagnosticEngine:
    """Evaluates quiz submissions, diagnoses underlying student misconceptions, and produces reports."""

    def __init__(self, generator: AdaptiveAssessmentGenerator):
        self.generator = generator

    def evaluate_quiz(self, submission: QuizSubmission) -> Tuple[List[QuestionResult], Dict[str, Any]]:
        """
        Evaluates submitted answers, diagnoses misconceptions for incorrect choices,
        and generates cited corrective feedback.
        """
        results: List[QuestionResult] = []
        topic_stats: Dict[str, Dict[str, Any]] = {}
        misconceptions: List[Dict[str, str]] = []

        for q_id, student_ans in submission.answers.items():
            question = self.generator.get_question_by_id(q_id)
            if not question:
                continue

            student_ans_clean = student_ans.strip()
            is_correct = False
            diagnosed_misc = None

            if question.type == QuestionType.MCQ:
                # Check option letter (e.g. "A" or "A)")
                opt_letter = student_ans_clean[0].upper() if student_ans_clean else ""
                correct_letter = question.correct_answer[0].upper()
                is_correct = (opt_letter == correct_letter)
                if not is_correct and opt_letter in question.misconception_distractors:
                    diagnosed_misc = question.misconception_distractors[opt_letter]
                    misconceptions.append({
                        "question_id": q_id,
                        "topic_name": question.topic_name,
                        "selected_option": opt_letter,
                        "misconception": diagnosed_misc
                    })

            elif question.type == QuestionType.NUMERICAL:
                try:
                    s_val = float(re.findall(r"[-+]?\d*\.?\d+", student_ans_clean)[0])
                    c_val = float(question.correct_answer)
                    tol = question.tolerance if question.tolerance is not None else 0.05
                    is_correct = abs(s_val - c_val) <= tol
                except (IndexError, ValueError):
                    is_correct = False
                if not is_correct and "error" in question.misconception_distractors:
                    diagnosed_misc = question.misconception_distractors["error"]
                    misconceptions.append({
                        "question_id": q_id,
                        "topic_name": question.topic_name,
                        "selected_option": student_ans_clean,
                        "misconception": diagnosed_misc
                    })

            elif question.type == QuestionType.SHORT_ANSWER:
                # Semantic / keyword coverage rubric check
                keywords = [w.lower() for w in question.correct_answer.split() if len(w) > 4]
                match_count = sum(1 for kw in set(keywords) if kw in student_ans_clean.lower())
                coverage = match_count / max(1, len(set(keywords)))
                is_correct = coverage >= 0.40
                if not is_correct:
                    diagnosed_misc = f"Explanation missed critical concepts: {', '.join(keywords[:3])}."
                    misconceptions.append({
                        "question_id": q_id,
                        "topic_name": question.topic_name,
                        "selected_option": "Incomplete conceptual explanation",
                        "misconception": diagnosed_misc
                    })

            # Update topic stats
            t_id = question.topic_id
            if t_id not in topic_stats:
                topic_stats[t_id] = {
                    "topic_name": question.topic_name,
                    "total": 0,
                    "correct": 0,
                    "accuracy": 0.0
                }
            topic_stats[t_id]["total"] += 1
            if is_correct:
                topic_stats[t_id]["correct"] += 1

            results.append(QuestionResult(
                question_id=q_id,
                question_text=question.question_text,
                student_answer=student_ans_clean,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                citation_label=question.citation_label,
                solution_explanation=question.solution_explanation,
                misconception_diagnosed=diagnosed_misc,
                topic_id=question.topic_id,
                topic_name=question.topic_name
            ))

        # Calculate final accuracies
        for t_id, data in topic_stats.items():
            data["accuracy"] = round(data["correct"] / max(1, data["total"]), 2)

        return results, {
            "topic_stats": topic_stats,
            "misconceptions": misconceptions
        }
