"""
CLI Benchmark Runner:
Executes the RAGAS & DeepEval evaluation suite from the terminal
and prints metric reports and refusal accuracy.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ingestion.preloaded_course import get_preloaded_course
from app.grounding.retriever import HybridRetriever
from app.evaluation.eval_runner import SystemEvaluationRunner

def main():
    print("=" * 70)
    print("SYNAPSELEARN AI: SYSTEM EVALUATION & BENCHMARK RUNNER")
    print("Evaluating Grounding, Faithfulness, Relevancy & Refusal")
    print("=" * 70)

    course = get_preloaded_course()
    retriever = HybridRetriever(course.content_units)
    runner = SystemEvaluationRunner(retriever)

    print("\nRunning RAGAS evaluation over benchmark test suite...")
    report = runner.run_benchmark()
    m = report["summary_metrics"]

    print("\n" + "-" * 70)
    print("AGGREGATE RAGAS / DEEPEVAL METRICS SUMMARY:")
    print("-" * 70)
    print(f"  Composite Pipeline Score:          {m['overall_score'] * 100:.1f}%")
    print(f"  Faithfulness (Context Grounded):   {m['faithfulness'] * 100:.1f}%")
    print(f"  Answer Relevancy:                  {m['answer_relevancy'] * 100:.1f}%")
    print(f"  Context Precision (MRR):           {m['context_precision'] * 100:.1f}%")
    print(f"  Context Recall (Reference Facts):  {m['context_recall'] * 100:.1f}%")
    print(f"  Hallucination Refusal Accuracy:    {m['hallucination_refusal_rate'] * 100:.1f}% (Strict rejection of adversarial queries)")
    print(f"  Total Evaluated Items:             {m['total_queries_evaluated']} ({m['in_scope_queries']} in-scope, {m['adversarial_out_of_scope_queries']} adversarial)")
    print("-" * 70)

    print("\nINDIVIDUAL QUERY EVALUATION BREAKDOWN:")
    for item in report["item_breakdown"]:
        scope_tag = "[OFF-MATERIAL ADVERSARIAL]" if item["is_out_of_scope"] else "[IN-SCOPE]"
        ref_status = "DECLINED (OK)" if item["was_refused"] else f"GROUNDED ({item['retrieved_citation']})"
        print(f"  * {item['id']} {scope_tag:28s}: {item['query'][:45]}...")
        print(f"    Status: {ref_status:32s} | Precision: {item['context_precision']:.2f} | Faithfulness: {item['faithfulness']:.2f}")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
