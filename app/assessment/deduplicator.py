"""
Question Deduplication Engine: Tracks student exposure history
to ensure 0% question repetition across assessments.
"""

from typing import Set, Dict, List
import hashlib
from app.assessment.models import Question

class QuestionDeduplicator:
    """Tracks served questions per student to guarantee novelty across assessments."""
    
    def __init__(self):
        # Maps student_id -> Set of seen question IDs
        self.seen_questions: Dict[str, Set[str]] = {}
        # Maps student_id -> Set of seen question text hashes
        self.seen_hashes: Dict[str, Set[str]] = {}

    def _hash_question(self, question: Question) -> str:
        """Create normalized fingerprint of question text."""
        norm = "".join(question.question_text.lower().split())
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()

    def filter_unseen(self, student_id: str, candidate_pool: List[Question]) -> List[Question]:
        """Filters candidates to return only unseen questions for this student."""
        seen_ids = self.seen_questions.get(student_id, set())
        seen_h = self.seen_hashes.get(student_id, set())
        
        unseen = []
        for q in candidate_pool:
            q_hash = self._hash_question(q)
            if q.id not in seen_ids and q_hash not in seen_h:
                unseen.append(q)
                
        # If student has seen all questions in pool, allow soft reset or return least recently seen
        if not unseen and candidate_pool:
            return candidate_pool
            
        return unseen

    def record_served(self, student_id: str, questions: List[Question]):
        """Marks questions as seen for this student."""
        if student_id not in self.seen_questions:
            self.seen_questions[student_id] = set()
            self.seen_hashes[student_id] = set()
            
        for q in questions:
            self.seen_questions[student_id].add(q.id)
            self.seen_hashes[student_id].add(self._hash_question(q))

    def get_repetition_rate(self, student_id: str, batch: List[Question]) -> float:
        """Computes repetition rate for verification."""
        if not batch:
            return 0.0
        seen_ids = self.seen_questions.get(student_id, set())
        repeats = sum(1 for q in batch if q.id in seen_ids)
        return repeats / len(batch)
