"""
RAGAS & DeepEval Evaluation Framework Metrics
Implements Faithfulness, Answer Relevancy, Context Precision, Context Recall, and Refusal Accuracy.
"""

import re
import math
from typing import List, Dict, Any, Tuple

class RagasEvaluator:
    """Computes standard RAG evaluation framework metrics for retrieval and generation."""

    @staticmethod
    def compute_context_precision(retrieved_ids: List[str], ground_truth_id: str) -> float:
        """
        Rank-weighted context precision (MRR-style):
        1.0 if correct source is at rank 1, 0.5 at rank 2, 0.33 at rank 3, etc.
        """
        if not retrieved_ids or not ground_truth_id:
            return 0.0
        for rank, uid in enumerate(retrieved_ids):
            if ground_truth_id.lower() in uid.lower() or uid.lower() in ground_truth_id.lower():
                return round(1.0 / (rank + 1), 3)
        return 0.0

    @staticmethod
    def compute_context_recall(retrieved_text: str, ground_truth_facts: List[str]) -> float:
        """
        Calculates ratio of ground-truth reference facts recalled in the retrieved context.
        """
        if not ground_truth_facts:
            return 1.0
        r_text = retrieved_text.lower()
        matched = 0
        for fact in ground_truth_facts:
            # Check keywords in fact
            keywords = [w.lower() for w in re.findall(r"\b[a-z]{4,}\b", fact)]
            if any(k in r_text for k in keywords):
                matched += 1
        return round(matched / len(ground_truth_facts), 3)

    @staticmethod
    def compute_faithfulness(answer_text: str, retrieved_context: str) -> float:
        """
        Evaluates whether claims in generated answer are supported by retrieved context.
        Penalizes claims lacking source backing.
        """
        if "query declined" in answer_text.lower() or "outside the scope" in answer_text.lower():
            # Correct refusal is 100% faithful to the policy
            return 1.0
            
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", answer_text) if len(s.strip()) > 15]
        if not sentences:
            return 1.0
            
        supported = 0
        c_text = retrieved_context.lower()
        for sent in sentences:
            words = [w.lower() for w in re.findall(r"\b[a-z]{4,}\b", sent)]
            if not words:
                supported += 1
                continue
            # Check overlap with context
            overlap = sum(1 for w in words if w in c_text)
            if overlap / len(words) >= 0.30:
                supported += 1
                
        return round(supported / len(sentences), 3)

    @staticmethod
    def compute_answer_relevancy(question: str, answer_text: str) -> float:
        """
        Evaluates relevance of answer to user question using token overlap and intent alignment.
        """
        q_tokens = set(re.findall(r"\b[a-z]{3,}\b", question.lower()))
        if not q_tokens:
            return 1.0
        a_tokens = set(re.findall(r"\b[a-z]{3,}\b", answer_text.lower()))
        
        overlap = len(q_tokens.intersection(a_tokens))
        jaccard = overlap / max(1, len(q_tokens.union(a_tokens)))
        # Scale to standard 0-1 relevancy
        relevancy = min(1.0, 0.40 + jaccard * 1.5)
        return round(relevancy, 3)

    @staticmethod
    def evaluate_refusal_accuracy(is_out_of_scope: bool, was_refused: bool) -> float:
        """Evaluates whether adversarial / out-of-scope query was correctly refused."""
        if is_out_of_scope:
            return 1.0 if was_refused else 0.0
        else:
            return 1.0 if not was_refused else 0.0
