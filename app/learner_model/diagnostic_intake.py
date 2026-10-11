"""
Diagnostic Intake Engine: Onboards new students with zero history
using conversational intake and a 3-question diagnostic screening assessment.
"""

from typing import Dict, Any, List
from app.learner_model.bkt import LearnerModel
from app.assessment.models import Question, QuestionType, DifficultyLevel

DIAGNOSTIC_SCREENER_QUESTIONS = [
    Question(
        id="diag-01",
        topic_id="topic-1",
        topic_name="Loss Functions & Optimization Landscapes",
        type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        irt_difficulty_b=-1.0,
        irt_discrimination_a=1.0,
        question_text="If a scalar loss function L(w) has gradient dL/dw > 0 at current point w, which direction should w move to reduce the loss?",
        options=[
            "A) Decrease w (move in direction opposite to the gradient)",
            "B) Increase w (move in direction of the gradient)",
            "C) Keep w constant because gradient is positive",
            "D) Multiply w by the square of the Hessian"
        ],
        correct_answer="A",
        solution_explanation="Gradient descent updates w <- w - alpha * grad. If grad > 0, we subtract a positive value, decreasing w to move downhill.",
        misconception_distractors={
            "B": "Direction inversion: Moving in direction of the gradient performs Gradient Ascent, which maximizes loss rather than minimizing it."
        },
        citation_label="Textbook Ch 1, p. 18",
        source_unit_id="unit-tb-01"
    ),
    Question(
        id="diag-02",
        topic_id="topic-3",
        topic_name="Multi-Layer Perceptrons & Backpropagation",
        type=QuestionType.MCQ,
        difficulty=DifficultyLevel.MEDIUM,
        irt_difficulty_b=0.0,
        irt_discrimination_a=1.1,
        question_text="If a neural network with multiple hidden layers uses exclusively linear activation functions f(z) = z, what mathematical class of mapping does the entire network compute?",
        options=[
            "A) A single linear transformation, regardless of depth.",
            "B) A high-degree polynomial non-linear transformation.",
            "C) A piecewise step function.",
            "D) A universal non-linear approximation."
        ],
        correct_answer="A",
        solution_explanation="The composition of any number of linear functions is strictly linear: W_2(W_1 x + b_1) + b_2 = (W_2 W_1)x + (W_2 b_1 + b_2). Without non-linear activations, depth provides no representational power.",
        misconception_distractors={
            "B": "Linearity composition confusion: Stacking linear layers cannot generate polynomials or non-linear curves."
        },
        citation_label="Textbook Ch 3, p. 68",
        source_unit_id="unit-tb-03"
    ),
    Question(
        id="diag-03",
        topic_id="topic-4",
        topic_name="Convolutional Neural Networks (CNNs)",
        type=QuestionType.MCQ,
        difficulty=DifficultyLevel.MEDIUM,
        irt_difficulty_b=0.2,
        irt_discrimination_a=1.2,
        question_text="What key inductive bias of images do Convolutional Neural Networks exploit compared to fully connected layers?",
        options=[
            "A) Translation invariance and spatial locality of pixel features.",
            "B) Permutation equivariance across token positions.",
            "C) Complete independence among adjacent pixels.",
            "D) Strict temporal recurrence across time steps."
        ],
        correct_answer="A",
        solution_explanation="CNNs utilize parameter sharing (translation invariance) and localized kernels (spatial locality) because neighboring pixels are strongly correlated regardless of where a feature appears in an image.",
        misconception_distractors={
            "B": "Transformer confusion: Permutation equivariance is a property of self-attention, not convolutions."
        },
        citation_label="Lecture 3 @ 09:20",
        source_unit_id="unit-v3-01"
    )
]

class DiagnosticIntakeManager:
    """Manages the zero-history onboarding survey and initial prior calibration."""

    @staticmethod
    def get_diagnostic_questions() -> List[Question]:
        return DIAGNOSTIC_SCREENER_QUESTIONS

    @staticmethod
    def calibrate_new_student(
        student_id: str,
        self_reported_level: str, # "beginner", "intermediate", "advanced"
        diagnostic_score: int,    # 0 to 3
        course_topic_ids: List[str]
    ) -> LearnerModel:
        """
        Calibrates initial BKT priors and IRT ability theta for a student with no prior history.
        """
        model = LearnerModel(student_id=student_id)
        
        # Base settings from self-reported background
        if self_reported_level == "beginner":
            base_prior = 0.15
            theta = -1.2
        elif self_reported_level == "advanced":
            base_prior = 0.60
            theta = 1.0
        else: # intermediate
            base_prior = 0.35
            theta = 0.0

        # Adjust based on diagnostic screener (score out of 3)
        screener_adjustment = (diagnostic_score - 1.5) * 0.10
        final_prior = max(0.10, min(0.80, base_prior + screener_adjustment))
        final_theta = theta + (diagnostic_score - 1.5) * 0.50

        model.ability_theta = round(final_theta, 2)

        # Initialize BKT state for all course topics
        for idx, tid in enumerate(course_topic_ids):
            # Prerequisite topics start with slightly higher prior than advanced topics (e.g. Transformers)
            topic_decay = idx * 0.04
            topic_prior = max(0.08, final_prior - topic_decay)
            state = model.get_or_create_topic_state(tid, f"Topic {idx+1}", prior=topic_prior)
            state.p_mastery = round(topic_prior, 3)
            state.history[0]["p_mastery"] = round(topic_prior, 3)

        return model
