"""
Multi-Session Student Simulation Engine:
Simulates multiple student profiles (Novice, Intermediate, Fast-Learner) across sequential sessions
to quantitatively evaluate personalization, BKT mastery gains, and question repetition rates.
"""

from typing import Dict, List, Any
import random
from app.learner_model.bkt import LearnerModel
from app.assessment.generator import AdaptiveAssessmentGenerator
from app.assessment.deduplicator import QuestionDeduplicator

class SimulatedStudentProfile:
    """Configurable agent representing a synthetic student."""
    def __init__(
        self,
        profile_name: str,
        initial_prior: float,
        p_transit: float,
        p_slip: float,
        p_guess: float,
        initial_theta: float
    ):
        self.profile_name = profile_name
        self.initial_prior = initial_prior
        self.p_transit = p_transit
        self.p_slip = p_slip
        self.p_guess = p_guess
        self.initial_theta = initial_theta

SIMULATED_PROFILES: Dict[str, SimulatedStudentProfile] = {
    "novice": SimulatedStudentProfile(
        profile_name="Novice / Struggling Learner",
        initial_prior=0.15,
        p_transit=0.12,
        p_slip=0.20,
        p_guess=0.15,
        initial_theta=-1.2
    ),
    "intermediate": SimulatedStudentProfile(
        profile_name="Intermediate / Steady Learner",
        initial_prior=0.35,
        p_transit=0.20,
        p_slip=0.10,
        p_guess=0.20,
        initial_theta=0.0
    ),
    "advanced": SimulatedStudentProfile(
        profile_name="Advanced / Fast Learner",
        initial_prior=0.60,
        p_transit=0.32,
        p_slip=0.05,
        p_guess=0.25,
        initial_theta=1.2
    )
}

class MultiSessionSimulator:
    """Executes multi-session longitudinal simulations for personalization benchmarks."""

    def __init__(self, course_topic_ids: List[str]):
        self.course_topic_ids = course_topic_ids

    def run_simulation(
        self,
        profile_key: str = "intermediate",
        num_sessions: int = 5,
        questions_per_session: int = 2
    ) -> Dict[str, Any]:
        """
        Executes a sequence of learning & assessment sessions for a simulated student profile.
        Returns trajectory of BKT mastery, IRT ability, accuracy, and question repetition count.
        """
        profile = SIMULATED_PROFILES.get(profile_key, SIMULATED_PROFILES["intermediate"])
        deduplicator = QuestionDeduplicator()
        generator = AdaptiveAssessmentGenerator(deduplicator=deduplicator)
        
        sim_student_id = f"sim_{profile_key}_{random.randint(1000, 9999)}"
        learner_model = LearnerModel(student_id=sim_student_id)
        learner_model.ability_theta = profile.initial_theta

        # Initialize BKT topic states
        for tid in self.course_topic_ids:
            state = learner_model.get_or_create_topic_state(
                tid,
                f"Topic {tid}",
                prior=profile.initial_prior
            )
            state.p_transit = profile.p_transit
            state.p_slip = profile.p_slip
            state.p_guess = profile.p_guess

        sessions_data = []
        all_served_question_ids = []
        repeat_count = 0

        current_avg_mastery = profile.initial_prior

        for session_idx in range(1, num_sessions + 1):
            # Generate adaptive questions
            questions = generator.generate_quiz(
                student_id=sim_student_id,
                num_questions=questions_per_session
            )

            # Check for repeats
            session_repeats = sum(1 for q in questions if q.id in all_served_question_ids)
            repeat_count += session_repeats
            all_served_question_ids.extend([q.id for q in questions])

            session_correct = 0
            # Simulate answers based on profile dynamics
            for q in questions:
                # Probability student knows the concept
                curr_topic_mastery = learner_model.get_or_create_topic_state(q.topic_id, q.topic_name).p_mastery
                p_correct = curr_topic_mastery * (1.0 - profile.p_slip) + (1.0 - curr_topic_mastery) * profile.p_guess
                
                is_correct = random.random() < p_correct
                if is_correct:
                    session_correct += 1

                # Update BKT
                learner_model.record_quiz_answer(q.topic_id, q.topic_name, is_correct)

            # Ability update
            ability_delta = (session_correct / max(1, len(questions)) - 0.5) * 0.4
            learner_model.ability_theta = round(learner_model.ability_theta + ability_delta, 2)

            mastery_dict = learner_model.get_all_mastery()
            current_avg_mastery = sum(mastery_dict.values()) / max(1, len(mastery_dict))

            sessions_data.append({
                "session": session_idx,
                "questions_answered": len(questions),
                "correct_answers": session_correct,
                "session_accuracy": round(session_correct / max(1, len(questions)), 2),
                "average_bkt_mastery": round(current_avg_mastery, 3),
                "estimated_theta": learner_model.ability_theta,
                "question_repeats": session_repeats
            })

        total_questions = len(all_served_question_ids)
        repetition_rate = round(repeat_count / max(1, total_questions), 4)
        net_mastery_gain = round(current_avg_mastery - profile.initial_prior, 3)

        return {
            "profile_name": profile.profile_name,
            "initial_prior": profile.initial_prior,
            "final_mastery": round(current_avg_mastery, 3),
            "net_mastery_gain": net_mastery_gain,
            "total_questions_served": total_questions,
            "total_repeated_questions": repeat_count,
            "question_repetition_rate": repetition_rate,
            "sessions": sessions_data
        }
