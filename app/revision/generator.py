"""
Smart Revision Suite:
Generates targeted flashcards, topic cheat-sheets, exam study schedules,
and audio briefs for spaced repetition review.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from app.services.ai_service import AIService

PRELOADED_FLASHCARDS = [
    {
        "id": "fc-01",
        "topic_id": "topic-1",
        "topic_name": "Loss Functions & Optimization Landscapes",
        "front": "Why is Cross-Entropy Loss preferred over MSE for Softmax classification outputs?",
        "back": "Cross-Entropy avoids gradient vanishing when predictions are confidently wrong because dL/dz = y_hat - y (linear error), whereas MSE has a sigma'(z) factor that saturates to 0.",
        "citation": "Slide Deck 1, Slide 7",
        "box": 1
    },
    {
        "id": "fc-02",
        "topic_id": "topic-2",
        "topic_name": "Gradient Descent & Adaptive Optimizers",
        "front": "What does Adam's bias correction formula m_hat = m_t / (1 - beta_1^t) fix?",
        "back": "Because moment vectors are initialized at zero, early moving averages are heavily biased towards zero. Dividing by (1 - beta^t) provides an unbiased gradient estimate in initial steps.",
        "citation": "Textbook Ch 2, p. 45",
        "box": 2
    },
    {
        "id": "fc-03",
        "topic_id": "topic-3",
        "topic_name": "Multi-Layer Perceptrons & Backpropagation",
        "front": "Why does ReLU prevent vanishing gradients compared to Sigmoid in deep networks?",
        "back": "Sigmoid's derivative peaks at only 0.25 (multiplying across 10 layers shrinks gradients to 10^-6). ReLU's derivative is exactly 1.0 for all z > 0, allowing gradients to propagate unattenuated.",
        "citation": "Textbook Ch 3, p. 68",
        "box": 3
    },
    {
        "id": "fc-04",
        "topic_id": "topic-4",
        "topic_name": "Convolutional Neural Networks (CNNs)",
        "front": "What is the spatial output size formula for a 2D convolution layer?",
        "back": "O = floor((W - K + 2P)/S) + 1, where W is input dimension, K is kernel size, P is padding, and S is stride.",
        "citation": "Lecture 3 @ 09:20",
        "box": 2
    },
    {
        "id": "fc-05",
        "topic_id": "topic-5",
        "topic_name": "Sequence Modeling & Recurrent Networks",
        "front": "How does the LSTM cell state C_t solve the long-term dependency bottleneck?",
        "back": "The cell state acts as a linear conveyor belt: C_t = f_t * C_{t-1} + i_t * C_tilde. Backpropagation flows through time additively without repeated matrix multiplications that cause exponential vanishing.",
        "citation": "Textbook Ch 5, p. 128",
        "box": 1
    },
    {
        "id": "fc-06",
        "topic_id": "topic-6",
        "topic_name": "Self-Attention & Transformer Architecture",
        "front": "Why is the dot-product Attention(Q, K, V) scaled by 1/sqrt(d_k)?",
        "back": "For large projection dimensions d_k, dot products grow large, pushing softmax into extreme regions with near-zero gradients. Scaling by 1/sqrt(d_k) preserves unit variance.",
        "citation": "Lecture 4 @ 29:15",
        "box": 3
    }
]

TOPIC_CHEAT_SHEETS = {
    "topic-1": {
        "title": "Loss Functions & Optimization Landscapes Cheat-Sheet",
        "key_formulas": [
            "L_MSE = (1/2N) sum (y_i - y_hat_i)^2",
            "L_CE = -sum y_i * log(y_hat_i)",
            "Hessian Condition Number: kappa = lambda_max / lambda_min"
        ],
        "core_insights": [
            "Never pair MSE with Softmax: gradients saturate when wrong.",
            "Ill-conditioned curvature causes SGD to bounce between steep canyon walls.",
            "Cross-Entropy yields linear gradient error: dL/dz = y_hat - y."
        ],
        "citations": ["Textbook Ch 1, p. 18", "Slide Deck 1, Slide 7"]
    },
    "topic-2": {
        "title": "Gradient Descent & Optimizers Cheat-Sheet",
        "key_formulas": [
            "Momentum: v_t = beta * v_{t-1} + (1-beta) * grad_t",
            "Adam: m_hat = m_t / (1 - beta_1^t), v_hat = v_t / (1 - beta_2^t)",
            "Update: theta_{t+1} = theta_t - alpha * m_hat / (sqrt(v_hat) + eps)"
        ],
        "core_insights": [
            "Polyak momentum cancels perpendicular oscillations and accelerates in consistent directions.",
            "Adam combines first (momentum) and second (RMSProp) moments with bias correction.",
            "Learning rate warmup stabilizes transformer training when initial gradient variances are high."
        ],
        "citations": ["Lecture 1 @ 21:40", "Textbook Ch 2, p. 45"]
    },
    "topic-3": {
        "title": "MLPs & Backpropagation Cheat-Sheet",
        "key_formulas": [
            "Chain Rule: dL/dx = sum_j (dL/dy_j * dy_j/dx)",
            "Sigmoid Derivative: sigma'(z) = sigma(z)(1 - sigma(z)) <= 0.25",
            "ReLU: f(z) = max(0, z) -> f'(z) = 1 for z > 0"
        ],
        "core_insights": [
            "Sigmoid vanishes exponentially in deep networks (0.25^N).",
            "ReLU solves saturation but can suffer from 'Dying ReLU' if z < 0 permanently.",
            "Leaky ReLU (alpha=0.01) and GELU provide non-zero pathways."
        ],
        "citations": ["Textbook Ch 3, p. 68", "Slide Deck 2, Slide 11"]
    },
    "topic-4": {
        "title": "Convolutional Neural Networks Cheat-Sheet",
        "key_formulas": [
            "Output Dimension: O = floor((W - K + 2P)/S) + 1",
            "ResNet Skip: H(x) = F(x) + x",
            "Backward Skip: dL/dx = dL/dH * (dF/dx + 1)"
        ],
        "core_insights": [
            "CNNs exploit spatial locality and parameter-shared translation invariance.",
            "Two stacked 3x3 convolutions match a 5x5 receptive field with 28% fewer weights.",
            "The '+1' additive identity in ResNet creates a gradient superhighway for 100+ layer networks."
        ],
        "citations": ["Lecture 3 @ 09:20", "Textbook Ch 4, p. 102"]
    },
    "topic-5": {
        "title": "Sequence Models & LSTMs Cheat-Sheet",
        "key_formulas": [
            "Forget Gate: f_t = sigma(W_f [h_{t-1}, x_t] + b_f)",
            "Cell State: C_t = f_t * C_{t-1} + i_t * C_tilde_t",
            "Hidden State: h_t = o_t * tanh(C_t)"
        ],
        "core_insights": [
            "Vanilla RNN backpropagates through (W_hh)^T, causing exponential vanishing/explosion.",
            "LSTM constant error carousel preserves long-range information when f_t = 1.",
            "BPTT truncates past time steps to limit compute memory."
        ],
        "citations": ["Lecture 4 @ 12:10", "Textbook Ch 5, p. 128"]
    },
    "topic-6": {
        "title": "Transformers & Self-Attention Cheat-Sheet",
        "key_formulas": [
            "Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V",
            "MultiHead = Concat(head_1, ..., head_h) W^O",
            "Positional Encoding: PE(pos, 2i) = sin(pos / 10000^(2i/d))"
        ],
        "core_insights": [
            "Scaling by 1/sqrt(d_k) prevents softmax gradient saturation.",
            "Self-attention is permutation-equivariant, requiring sinusoidal or rotary positional encodings.",
            "Attention complexity scales quadratically O(N^2 * d) with sequence length N."
        ],
        "citations": ["Lecture 4 @ 29:15", "Textbook Ch 6, p. 154"]
    }
}

class RevisionSuiteManager:
    """Manages flashcards, cheat-sheets, study schedules, and audio briefs."""

    @staticmethod
    def get_flashcards(topic_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if topic_id:
            return [fc for fc in PRELOADED_FLASHCARDS if fc["topic_id"] == topic_id]
        return PRELOADED_FLASHCARDS

    @staticmethod
    def get_cheat_sheet(topic_id: str) -> Optional[Dict[str, Any]]:
        return TOPIC_CHEAT_SHEETS.get(topic_id, None)

    @staticmethod
    def generate_study_schedule(
        weak_topic_ids: List[str],
        days_until_exam: int = 7,
        hours_per_day: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Creates an adaptive study plan distributing revision time based on
        student weaknesses and forgetting curve urgency.
        """
        all_topics = list(TOPIC_CHEAT_SHEETS.keys())
        # Prioritize weak topics first, then remaining topics
        ordered_topics = [t for t in weak_topic_ids if t in all_topics]
        for t in all_topics:
            if t not in ordered_topics:
                ordered_topics.append(t)

        schedule = []
        start_date = datetime.now()

        for day in range(1, days_until_exam + 1):
            date_str = (start_date + timedelta(days=day-1)).strftime("%A, %b %d")
            # Assign primary topic
            topic_idx = (day - 1) % len(ordered_topics)
            primary_topic_id = ordered_topics[topic_idx]
            sheet = TOPIC_CHEAT_SHEETS.get(primary_topic_id, {})
            is_weak = primary_topic_id in weak_topic_ids

            tasks = [
                f"Review {sheet.get('title', primary_topic_id)} formulas",
                f"Practice 4 adaptive quiz questions on {primary_topic_id}",
                "Review Leitner Box 1 flashcards"
            ]
            if is_weak:
                tasks.insert(0, "⚠️ Priority Focus: Read textbook cited pages & rewatch lecture segment")

            schedule.append({
                "day": day,
                "date": date_str,
                "allocated_hours": hours_per_day,
                "primary_topic_id": primary_topic_id,
                "topic_title": sheet.get("title", primary_topic_id),
                "is_weak_topic": is_weak,
                "tasks": tasks
            })

        return schedule

    @staticmethod
    def generate_audio_brief(topic_id: str) -> Dict[str, Any]:
        """Generates audio brief script and key highlights for speech synthesis."""
        sheet = TOPIC_CHEAT_SHEETS.get(topic_id, TOPIC_CHEAT_SHEETS["topic-1"])
        script = (
            f"Welcome to your 2-minute Audio Brief on {sheet['title']}. "
            "Here are the three foundational takeaways from your course material. "
            f"Point 1: {sheet['core_insights'][0]} "
            f"Point 2: {sheet['core_insights'][1]} "
            f"Point 3: {sheet['core_insights'][2]} "
            f"For in-depth mathematical formulas, refer to your course textbook citations: {', '.join(sheet['citations'])}. "
            "Good luck with your study session!"
        )
        return {
            "topic_id": topic_id,
            "title": f"Audio Brief: {sheet['title']}",
            "duration_est": "2 minutes",
            "script": script,
            "citations": sheet["citations"]
        }

    @staticmethod
    async def generate_ai_flashcards(
        topic_id: str = "topic-1",
        num_cards: int = 3,
        api_key_override: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Dynamically generates novel Leitner flashcards using Gemini or local syllabus synthesis."""
        cards: List[Dict[str, Any]] = []
        sheet = TOPIC_CHEAT_SHEETS.get(topic_id, TOPIC_CHEAT_SHEETS["topic-1"])
        topic_title = sheet["title"].replace(" Cheat-Sheet", "")

        ai_items = await AIService.generate_flashcards(
            topic_name=topic_title,
            num_cards=num_cards,
            api_key_override=api_key_override
        )
        if ai_items and isinstance(ai_items, list):
            for idx, it in enumerate(ai_items):
                cards.append({
                    "id": f"ai-fc-{uuid.uuid4().hex[:6]}",
                    "topic_id": topic_id,
                    "topic_name": topic_title,
                    "front": it.get("front", ""),
                    "back": it.get("back", ""),
                    "citation": it.get("citation", sheet["citations"][0]),
                    "box": int(it.get("box", (idx % 3) + 1))
                })

        if not cards:
            # Algorithmic syllabus synthesis fallback
            pool = [
                {
                    "front": f"What is the foundational mathematical objective of {sheet['title'].replace(' Cheat-Sheet', '')}?",
                    "back": f"Core Formula: {sheet['key_formulas'][0]}. Insight: {sheet['core_insights'][0]}",
                    "citation": sheet["citations"][0]
                },
                {
                    "front": f"What is the most frequent misconception or architectural failure in {sheet['title'].replace(' Cheat-Sheet', '')}?",
                    "back": f"Key Pitfall to Avoid: {sheet['core_insights'][1]}",
                    "citation": sheet["citations"][-1]
                },
                {
                    "front": f"How does the secondary update rule ({sheet['key_formulas'][1] if len(sheet['key_formulas']) > 1 else sheet['key_formulas'][0]}) prevent training stagnation?",
                    "back": f"Mechanical Principle: {sheet['core_insights'][-1]}",
                    "citation": sheet["citations"][0]
                }
            ]
            for idx, item in enumerate(pool[:num_cards]):
                cards.append({
                    "id": f"ai-fc-{uuid.uuid4().hex[:6]}",
                    "topic_id": topic_id,
                    "topic_name": sheet["title"].replace(" Cheat-Sheet", ""),
                    "front": item["front"],
                    "back": item["back"],
                    "citation": item["citation"],
                    "box": (idx % 3) + 1
                })

        return cards

    @staticmethod
    async def generate_ai_cheat_sheet(
        topic_id: str,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dynamically generates high-yield exam cheat-sheet using Generative AI."""
        sheet = TOPIC_CHEAT_SHEETS.get(topic_id, {})
        topic_title = sheet.get("title", f"Topic {topic_id}").replace(" Cheat-Sheet", "")
        ai_res = await AIService.generate_cheat_sheet(
            topic_name=topic_title,
            api_key_override=api_key_override
        )
        if ai_res and isinstance(ai_res, dict) and "key_formulas" in ai_res:
            return ai_res
        return TOPIC_CHEAT_SHEETS.get(topic_id, TOPIC_CHEAT_SHEETS["topic-1"])

    @staticmethod
    async def generate_ai_audio_brief(
        topic_id: str,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synthesizes a 2-minute spoken conversational audio brief script using Generative AI."""
        sheet = TOPIC_CHEAT_SHEETS.get(topic_id, TOPIC_CHEAT_SHEETS["topic-1"])
        topic_title = sheet.get("title", f"Topic {topic_id}").replace(" Cheat-Sheet", "")
        ai_res = await AIService.generate_audio_brief(
            topic_name=topic_title,
            api_key_override=api_key_override
        )
        if ai_res and isinstance(ai_res, dict) and "script" in ai_res:
            return {
                "topic_id": topic_id,
                "title": ai_res.get("title", f"Audio Brief: {topic_title}"),
                "duration_est": ai_res.get("duration_est", "2 minutes"),
                "script": ai_res.get("script", ""),
                "citations": ai_res.get("citations", sheet.get("citations", []))
            }
        return RevisionSuiteManager.generate_audio_brief(topic_id)

    @staticmethod
    async def generate_ai_study_schedule(
        weak_topic_ids: List[str],
        days_until_exam: int = 7,
        hours_per_day: float = 2.0,
        api_key_override: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generates an AI personalized study plan prioritizing weak topics via Gemini."""
        all_topics = list(TOPIC_CHEAT_SHEETS.keys())
        ai_schedule = await AIService.generate_study_schedule(
            weak_topics=weak_topic_ids,
            all_topics=all_topics,
            days_until_exam=days_until_exam,
            hours_per_day=hours_per_day,
            api_key_override=api_key_override
        )
        if ai_schedule and isinstance(ai_schedule, list) and len(ai_schedule) > 0:
            return ai_schedule
        return RevisionSuiteManager.generate_study_schedule(
            weak_topic_ids=weak_topic_ids,
            days_until_exam=days_until_exam,
            hours_per_day=hours_per_day
        )

