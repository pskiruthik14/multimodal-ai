"""
Benchmark Test Set for Grounding & Evaluation
Contains in-scope questions with known ground-truth citations, plus adversarial off-material queries.
"""

from typing import List, Dict, Any
from pydantic import BaseModel

class BenchmarkQuery(BaseModel):
    id: str
    query: str
    is_out_of_scope: bool
    expected_ground_truth_id: str
    expected_citation: str
    reference_facts: List[str]
    topic_id: str

BENCHMARK_TEST_SET: List[BenchmarkQuery] = [
    # ---------------- In-Scope Grounded Queries ----------------
    BenchmarkQuery(
        id="bm-01",
        query="Why does Adam optimizer use bias correction in early iterations?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-tb-02",
        expected_citation="Textbook Ch 2, p. 45",
        reference_facts=[
            "Moment vectors m_t and v_t are initialized to zero",
            "Dividing by (1 - beta^t) compensates for zero initialization bias",
            "Prevents early step sizes from being artificially small"
        ],
        topic_id="topic-2"
    ),
    BenchmarkQuery(
        id="bm-02",
        query="How does ResNet skip connection prevent vanishing gradients?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-tb-04",
        expected_citation="Textbook Ch 4, p. 102",
        reference_facts=[
            "H(x) = F(x) + x formulation",
            "Derivative contains +1 additive term",
            "Allows gradient to flow directly back through identity shortcut"
        ],
        topic_id="topic-4"
    ),
    BenchmarkQuery(
        id="bm-03",
        query="Why do we scale dot products by 1/sqrt(d_k) in Self-Attention?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-v4-02",
        expected_citation="Lecture 4 @ 29:15",
        reference_facts=[
            "Dot products grow large in magnitude for high dimensions",
            "Pushes softmax into regions with extremely small gradients",
            "Dividing by sqrt(d_k) restores unit variance"
        ],
        topic_id="topic-6"
    ),
    BenchmarkQuery(
        id="bm-04",
        query="Why is Cross-Entropy preferred over MSE for softmax classification?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-sl-01",
        expected_citation="Slide Deck 1, Slide 7",
        reference_facts=[
            "MSE gradient contains derivative of softmax which saturates",
            "Cross-entropy derivative is linear (y_hat - y)",
            "Avoids gradient vanishing when predictions are confidently wrong"
        ],
        topic_id="topic-1"
    ),
    BenchmarkQuery(
        id="bm-05",
        query="What is the role of the forget gate in an LSTM cell?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-v4-01",
        expected_citation="Lecture 4 @ 12:10",
        reference_facts=[
            "Computes sigmoid activation f_t between 0 and 1",
            "Multiplies previous cell state C_{t-1}",
            "Discards irrelevant past memory"
        ],
        topic_id="topic-5"
    ),
    BenchmarkQuery(
        id="bm-06",
        query="What is the Dying ReLU problem and how can we mitigate it?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-sl-03",
        expected_citation="Slide Deck 2, Slide 11",
        reference_facts=[
            "Neuron input falls below zero permanently",
            "Derivative is zero so weight updates cease",
            "Leaky ReLU or GELU solves this with non-zero slope"
        ],
        topic_id="topic-3"
    ),
    BenchmarkQuery(
        id="bm-07",
        query="What formula determines the spatial output dimension of a 2D convolution layer?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-v3-01",
        expected_citation="Lecture 3 @ 09:20",
        reference_facts=[
            "O = floor((W - K + 2P)/S) + 1",
            "Depends on kernel size K, padding P, and stride S",
            "Zero padding prevents spatial collapse"
        ],
        topic_id="topic-4"
    ),
    BenchmarkQuery(
        id="bm-08",
        query="Why do Transformers require Positional Encoding?",
        is_out_of_scope=False,
        expected_ground_truth_id="unit-tb-06",
        expected_citation="Textbook Ch 6, p. 154",
        reference_facts=[
            "Self-attention is permutation-equivariant",
            "Word order is critical for natural language syntax",
            "Sinusoidal positional encoding allows relative position learning"
        ],
        topic_id="topic-6"
    ),

    # ---------------- Adversarial / Off-Material Queries (Testing Refusal) ----------------
    BenchmarkQuery(
        id="bm-adv-01",
        query="What is the traditional recipe to bake a chocolate lava cake?",
        is_out_of_scope=True,
        expected_ground_truth_id="",
        expected_citation="[OUT_OF_SCOPE]",
        reference_facts=[],
        topic_id="none"
    ),
    BenchmarkQuery(
        id="bm-adv-02",
        query="Who was elected president of the French Republic in 1848?",
        is_out_of_scope=True,
        expected_ground_truth_id="",
        expected_citation="[OUT_OF_SCOPE]",
        reference_facts=[],
        topic_id="none"
    ),
    BenchmarkQuery(
        id="bm-adv-03",
        query="Explain the biological process of photosynthesis in green plants.",
        is_out_of_scope=True,
        expected_ground_truth_id="",
        expected_citation="[OUT_OF_SCOPE]",
        reference_facts=[],
        topic_id="none"
    ),
    BenchmarkQuery(
        id="bm-adv-04",
        query="What is the current Bitcoin cryptocurrency mining difficulty?",
        is_out_of_scope=True,
        expected_ground_truth_id="",
        expected_citation="[OUT_OF_SCOPE]",
        reference_facts=[],
        topic_id="none"
    )
]
