"""
Evaluation Framework Runner:
Runs automated RAGAS-style evaluation over the benchmark test set and produces metric reports.
"""

from typing import List, Dict, Any
from app.evaluation.benchmark_dataset import BENCHMARK_TEST_SET, BenchmarkQuery
from app.evaluation.ragas_metrics import RagasEvaluator
from app.grounding.retriever import HybridRetriever
from app.grounding.verifier import GroundingVerifier

class SystemEvaluationRunner:
    """Executes RAGAS-style evaluation over benchmark queries and outputs metrics."""

    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
        self.evaluator = RagasEvaluator()

    def run_benchmark(self) -> Dict[str, Any]:
        """Runs evaluation over all benchmark items and computes aggregate scores."""
        query_results = []
        
        precisions = []
        recalls = []
        faithfulness_scores = []
        relevancies = []
        refusal_scores = []
        
        in_scope_count = 0
        out_of_scope_count = 0

        for item in BENCHMARK_TEST_SET:
            # 1. Retrieve candidates
            retrieved = self.retriever.retrieve(item.query, top_k=3)
            retrieved_ids = [u[0].id for u in retrieved]
            combined_context = " ".join([u[0].text_content for u in retrieved])
            
            # 2. Check grounding & refusal
            verif = GroundingVerifier.check_query_grounding(item.query, retrieved)
            is_refused = not verif["is_grounded"]
            
            # 3. Simulate or generate answer
            if is_refused:
                answer_text = verif.get("refusal_message", "Query declined.")
            else:
                top_unit = retrieved[0][0]
                answer_text = f"Based on {top_unit.citation_label}: {top_unit.text_content[:250]}..."
                
            # 4. Compute metrics
            refusal_acc = self.evaluator.evaluate_refusal_accuracy(item.is_out_of_scope, is_refused)
            refusal_scores.append(refusal_acc)
            
            if item.is_out_of_scope:
                out_of_scope_count += 1
                c_prec = 1.0 if is_refused else 0.0
                c_rec = 1.0 if is_refused else 0.0
                faith = 1.0 if is_refused else 0.0
                rel = 1.0 if is_refused else 0.5
            else:
                in_scope_count += 1
                c_prec = self.evaluator.compute_context_precision(retrieved_ids, item.expected_ground_truth_id)
                c_rec = self.evaluator.compute_context_recall(combined_context, item.reference_facts)
                faith = self.evaluator.compute_faithfulness(answer_text, combined_context)
                rel = self.evaluator.compute_answer_relevancy(item.query, answer_text)
                
            precisions.append(c_prec)
            recalls.append(c_rec)
            faithfulness_scores.append(faith)
            relevancies.append(rel)
            
            query_results.append({
                "id": item.id,
                "query": item.query,
                "is_out_of_scope": item.is_out_of_scope,
                "was_refused": is_refused,
                "expected_citation": item.expected_citation,
                "retrieved_citation": retrieved[0][0].citation_label if retrieved and not is_refused else "[REFUSED]",
                "context_precision": c_prec,
                "context_recall": c_rec,
                "faithfulness": faith,
                "answer_relevancy": rel,
                "refusal_accuracy": refusal_acc
            })

        avg_precision = sum(precisions) / max(1, len(precisions))
        avg_recall = sum(recalls) / max(1, len(recalls))
        avg_faithfulness = sum(faithfulness_scores) / max(1, len(faithfulness_scores))
        avg_relevancy = sum(relevancies) / max(1, len(relevancies))
        avg_refusal = sum(refusal_scores) / max(1, len(refusal_scores))
        
        overall_score = (avg_precision + avg_recall + avg_faithfulness + avg_relevancy + avg_refusal) / 5.0

        return {
            "summary_metrics": {
                "overall_score": round(overall_score, 3),
                "context_precision": round(avg_precision, 3),
                "context_recall": round(avg_recall, 3),
                "faithfulness": round(avg_faithfulness, 3),
                "answer_relevancy": round(avg_relevancy, 3),
                "hallucination_refusal_rate": round(avg_refusal, 3),
                "total_queries_evaluated": len(BENCHMARK_TEST_SET),
                "in_scope_queries": in_scope_count,
                "adversarial_out_of_scope_queries": out_of_scope_count
            },
            "item_breakdown": query_results
        }
