"""
Bayesian Knowledge Tracing (BKT) Engine:
Mathematically tracks and updates per-topic student mastery estimates
based on sequential quiz responses and interactive tutoring dialogue.
"""

from typing import Dict, List, Any, Optional
from app.config import settings

class BKTTopicState:
    """State of knowledge tracing for a single topic."""
    def __init__(
        self,
        topic_id: str,
        topic_name: str,
        prior: float = None,
        p_transit: float = None,
        p_guess: float = None,
        p_slip: float = None
    ):
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.p_mastery = prior if prior is not None else settings.BKT_PRIOR
        self.p_transit = p_transit if p_transit is not None else settings.BKT_TRANSITION
        self.p_guess = p_guess if p_guess is not None else settings.BKT_GUESS
        self.p_slip = p_slip if p_slip is not None else settings.BKT_SLIP
        self.history: List[Dict[str, Any]] = [{
            "step": 0,
            "observation": "initial",
            "p_mastery": round(self.p_mastery, 3)
        }]

    def update(self, is_correct: bool, context_label: str = "quiz") -> float:
        """
        Applies Bayesian update rule followed by transition step:
        P(L_t | obs) = Bayes(P(L_{t-1}), obs)
        P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) * P(T)
        """
        p_l = self.p_mastery
        
        if is_correct:
            # Observation: Correct
            # P(Correct | L) = 1 - P(S)
            # P(Correct | ~L) = P(G)
            numerator = p_l * (1.0 - self.p_slip)
            denominator = numerator + (1.0 - p_l) * self.p_guess
        else:
            # Observation: Incorrect
            # P(Incorrect | L) = P(S)
            # P(Incorrect | ~L) = 1 - P(G)
            numerator = p_l * self.p_slip
            denominator = numerator + (1.0 - p_l) * (1.0 - self.p_guess)

        # Posterior probability of mastery given current observation
        p_l_given_obs = numerator / max(1e-9, denominator)
        
        # Transition projection for next opportunity
        p_next = p_l_given_obs + (1.0 - p_l_given_obs) * self.p_transit
        self.p_mastery = max(0.01, min(0.99, p_next))

        self.history.append({
            "step": len(self.history),
            "observation": "correct" if is_correct else "incorrect",
            "context": context_label,
            "p_mastery": round(self.p_mastery, 3)
        })
        return self.p_mastery

    def update_from_conversation(self, interaction_quality: float = 0.5):
        """
        Updates BKT from conversational tutoring dialogue.
        interaction_quality in [0.0, 1.0]: 0.0 = completely confused, 1.0 = deep conceptual insight.
        """
        is_positive = interaction_quality >= 0.50
        # Use milder transition for chat vs formal exam
        self.update(is_correct=is_positive, context_label="tutor_chat")


class LearnerModel:
    """Maintains student profile, per-topic BKT states, and mastery histories."""

    def __init__(self, student_id: str = "student_default"):
        self.student_id = student_id
        self.topic_states: Dict[str, BKTTopicState] = {}
        self.ability_theta: float = settings.IRT_DEFAULT_ABILITY
        self.quizzes_taken: int = 0
        self.total_questions_answered: int = 0
        self.total_correct: int = 0

    def get_or_create_topic_state(self, topic_id: str, topic_name: str, prior: float = None) -> BKTTopicState:
        if topic_id not in self.topic_states:
            self.topic_states[topic_id] = BKTTopicState(topic_id, topic_name, prior=prior)
        return self.topic_states[topic_id]

    def record_quiz_answer(self, topic_id: str, topic_name: str, is_correct: bool) -> float:
        """Updates BKT state after a quiz response."""
        state = self.get_or_create_topic_state(topic_id, topic_name)
        new_mastery = state.update(is_correct, context_label="quiz")
        self.total_questions_answered += 1
        if is_correct:
            self.total_correct += 1
        return new_mastery

    def get_all_mastery(self) -> Dict[str, float]:
        """Returns dictionary mapping topic_id -> p_mastery."""
        return {tid: round(s.p_mastery, 3) for tid, s in self.topic_states.items()}

    def get_mastery_summary(self) -> Dict[str, Any]:
        """Returns summary report of student's current knowledge model."""
        mastery_map = self.get_all_mastery()
        mastered_topics = [tid for tid, m in mastery_map.items() if m >= settings.BKT_MASTERY_THRESHOLD]
        weak_topics = [tid for tid, m in mastery_map.items() if m < 0.50]
        
        return {
            "student_id": self.student_id,
            "ability_theta": round(self.ability_theta, 2),
            "mastery_by_topic": mastery_map,
            "mastered_topics_count": len(mastered_topics),
            "weak_topics_count": len(weak_topics),
            "total_questions_answered": self.total_questions_answered,
            "accuracy": round(self.total_correct / max(1, self.total_questions_answered), 2),
            "quizzes_taken": self.quizzes_taken
        }
