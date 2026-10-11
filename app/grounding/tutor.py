"""
Grounded Tutor Companion Engine:
Handles chat interactions, strict grounding, out-of-scope refusals,
multi-persona pedagogical AI modes (Professor, Feynman/ELI5, Socratic, Exam Cram, Hinglish),
and deep citation generation.
"""

from typing import Dict, Any, List, Optional
import httpx
from app.ingestion.models import Course, ContentUnit
from app.grounding.retriever import HybridRetriever
from app.grounding.verifier import GroundingVerifier
from app.grounding.citation_engine import CitationEngine
from app.grounding.bilingual import BilingualEngine
from app.learner_model.bkt import LearnerModel
from app.services.ai_service import AIService
from app.config import settings

PERSONA_SYSTEM_INSTRUCTIONS = {
    "professor": (
        "You are SynapseLearn AI in Professor persona: Deliver rigorous academic explanations "
        "with formal mathematical definitions, theorems, LaTeX equations, and precise citations. "
        "Maintain high intellectual depth and academic authority."
    ),
    "feynman": (
        "You are SynapseLearn AI in Feynman (ELI5) persona: Explain concepts intuitively using vivid, "
        "memorable real-world analogies, simple relatable language, and step-by-step physical intuition. "
        "Avoid unnecessary jargon while preserving exact course citations."
    ),
    "socratic": (
        "You are SynapseLearn AI in Socratic Tutor persona: Do not merely give away the answer! "
        "Instead, scaffold the student's thinking with 2-3 guided diagnostic questions, conceptual hints, "
        "and point them toward the cited material to deduce the principle themselves."
    ),
    "cram": (
        "You are SynapseLearn AI in Exam Cram persona: Provide ultra-concise, high-density bulleted "
        "cheat-sheet notes, core mathematical formulas, and the top 2 exam pitfalls/misconceptions to avoid. "
        "Keep it punchy, actionable, and cite the exact source."
    )
}

FEYNMAN_ANALOGIES = {
    "topic-1": (
        "💡 **Feynman Intuition (ELI5 Analogy):**\n"
        "Imagine an archery student shooting at a bullseye. With **MSE**, if the arrow hits the grass instead of the target, "
        "the coach whispers softly because the slope vanishes when you are totally off! But with **Cross-Entropy**, "
        "if you shoot in the complete opposite direction, a loud alarm sounds and gives you a massive, clear shove in the right direction. "
        "That is why classifiers never fall asleep when paired with Cross-Entropy!"
    ),
    "topic-2": (
        "💡 **Feynman Intuition (ELI5 Analogy):**\n"
        "Think of navigating down a foggy mountain ravine. Standard **SGD** is a cautious hiker who takes tiny steps and keeps bouncing "
        "left-and-right between the steep canyon walls. **Momentum** gives the hiker a heavy rolling bowling ball: side-to-side bounces "
        "cancel each other out, while downhill momentum builds up speed!\n"
        "**Adam** is like giving the hiker an adaptive speedometer for every single muscle: it scales down steps on steep slopes "
        "and speeds up on flat plateaus, with bias-correction making sure you don't stall on your very first step."
    ),
    "topic-3": (
        "💡 **Feynman Intuition (ELI5 Analogy):**\n"
        "Think of **Backpropagation** like a chain of students passing a message backwards about who made a mistake on a group test. "
        "With **Sigmoid**, every person mumbles the message down to 25% volume ($0.25$). By the 5th person, the whisper is completely inaudible (Vanishing Gradient!). "
        "**ReLU** is like a megaphone: whenever someone has a positive contribution, they yell with 100% volume ($slope = 1$), so the message travels across 100 layers without fading!"
    ),
    "topic-4": (
        "💡 **Feynman Intuition (ELI5 Analogy):**\n"
        "Think of a **CNN** like looking through a magnifying glass that slides across a painting, recognizing tiny brushstrokes (edges) first, "
        "then shapes, then full faces. And **ResNet**? Imagine a 100-story building where you can either take the stairs through every single room (slow and exhausting) "
        "or jump on an express elevator (+x shortcut) that takes you straight to the top floor with zero resistance!"
    ),
    "topic-5": (
        "💡 **Feynman Intuition (ELI5 Analogy):**\n"
        "Think of an **LSTM** like an executive with an assistant and a notebook (the Cell State $C_t$). Vanilla RNN tries to memorize everything in their head "
        "and forgets last week's meeting. In LSTM, the **Forget Gate** shreds irrelevant old notes, the **Input Gate** staples in new crucial facts, "
        "and the notebook stays preserved for months on end!"
    ),
    "topic-6": (
        "💡 **Feynman Intuition (ELI5 Analogy):**\n"
        "Think of **Self-Attention** like a roundtable dinner party where everyone can look across the table and make eye contact with every other guest at the same time. "
        "Each guest has a Question (Query $Q$), a Name-tag (Key $K$), and their Story (Value $V$). When your Question matches someone's Name-tag, you listen intently to their Story. "
        "And the $\\frac{1}{\\sqrt{d_k}}$ scaling factor? It prevents the loudest person in the room from shouting so loud that everyone else gets drowned out into silence!"
    )
}

SOCRATIC_HINTS = {
    "topic-1": (
        "🏛️ **Socratic Guided Inquiry:**\n"
        "Let's deduce this together from first principles!\n"
        "1. Consider what happens when a Softmax network outputs a probability $p \\approx 0$ for a true class $y = 1$. What is the derivative $\\sigma'(z)$ of the activation?\n"
        "2. If you multiply that derivative into your loss gradient in MSE, what happens to the magnitude of the weight update?\n"
        "3. Now look at the derivative of $-\\ln(p)$ in Cross-Entropy. Does it cancel out that problematic vanishing factor?\n\n"
        "👉 *Check the citation below to inspect the mathematical derivation!*"
    ),
    "topic-2": (
        "🏛️ **Socratic Guided Inquiry:**\n"
        "Let's trace how Adam builds its velocity!\n"
        "1. At step $t=1$, what is the initial value of $m_0$ before any gradients are observed?\n"
        "2. If $m_1 = 0.9 \\times 0 + 0.1 \\times g_1 = 0.1 g_1$, is this a fair estimate of the true average gradient, or is it heavily dragged toward zero?\n"
        "3. What division factor would scale $0.1 g_1$ back to the full $1.0 g_1$ at step $1$?\n\n"
        "👉 *Inspect the formula in the citation below to see why $(1 - \\beta^t)$ is the exact answer!*"
    ),
    "topic-3": (
        "🏛️ **Socratic Guided Inquiry:**\n"
        "Let's analyze the chain rule across 10 layers:\n"
        "1. Recall that $\\sigma'(z) = \\sigma(z)(1 - \\sigma(z))$. What is the absolute maximum value this derivative can ever reach?\n"
        "2. What is $0.25^{10}$? What does that do to the gradient reaching layer 1?\n"
        "3. For ReLU, what is $\\frac{d}{dz} \\max(0, z)$ when $z > 0$?\n\n"
        "👉 *Notice how the slope never decays! See the cited textbook section for the proof.*"
    ),
    "topic-4": (
        "🏛️ **Socratic Guided Inquiry:**\n"
        "Let's examine gradient flow in deep architectures:\n"
        "1. When training a standard plain 50-layer network, why does training error actually get *worse* than a 20-layer network?\n"
        "2. In ResNet, the output is $\\mathcal{H}(x) = \\mathcal{F}(x) + x$. When taking the derivative $\\frac{\\partial \\mathcal{H}}{\\partial x}$, what does the $+x$ term turn into?\n"
        "3. Can a sum containing $+1$ ever decay to zero even if $\\frac{\\partial \\mathcal{F}}{\\partial x}$ is near zero?\n\n"
        "👉 *Inspect the residual block diagram citation to see the gradient pathway.*"
    ),
    "topic-5": (
        "🏛️ **Socratic Guided Inquiry:**\n"
        "Let's analyze sequence memory:\n"
        "1. In a vanilla RNN, computing $h_t$ involves multiplying by weight matrix $W$ at every single time step. What happens when you multiply a matrix by itself 100 times?\n"
        "2. In an LSTM cell state update $C_t = f_t C_{t-1} + i_t \\tilde{C}_t$, is the interaction multiplicative or additive?\n"
        "3. When $f_t = 1$, does the gradient flow across time with or without attenuation?\n\n"
        "👉 *Review the LSTM gating diagram in your course citation below.*"
    ),
    "topic-6": (
        "🏛️ **Socratic Guided Inquiry:**\n"
        "Let's reason about attention scaling:\n"
        "1. If $q$ and $k$ are independent vectors with zero mean and variance $1$, what is the variance of their dot product $\\sum_{i=1}^{d_k} q_i k_i$?\n"
        "2. When dot products grow large (e.g. into the hundreds), what happens to the output of the Softmax function? Where does the derivative of Softmax go at extreme values?\n"
        "3. Why is dividing by $\\sqrt{d_k}$ the mathematically exact normalizer to restore unit variance?\n\n"
        "👉 *Check the Attention equation in the citation below.*"
    )
}

EXAM_CRAM_SUMMARIES = {
    "topic-1": (
        "⚡ **High-Yield Exam Cram: Loss Functions & Convexity**\n\n"
        "📌 **Must-Know Formula:**\n"
        "- Cross-Entropy Gradient: $\\frac{\\partial L}{\\partial z} = \\hat{y} - y$ (Linear error response!)\n\n"
        "⚠️ **Top Exam Traps & Misconceptions:**\n"
        "1. *Trap:* Thinking deep networks become convex when using Cross-Entropy. (FALSE: Hidden layers always induce non-convexity!).\n"
        "2. *Trap:* Claiming MSE uses more memory than Cross-Entropy. (FALSE: Difference is gradient saturation, not RAM!).\n\n"
        "🎯 **Exam Mnemonics:** Never pair Softmax with MSE in classification."
    ),
    "topic-2": (
        "⚡ **High-Yield Exam Cram: Optimizers (SGD, Momentum, Adam)**\n\n"
        "📌 **Must-Know Formula:**\n"
        "- Bias-corrected 1st moment: $\\hat{m}_t = \\frac{m_t}{1 - \\beta_1^t}$\n"
        "- Update: $\\theta_{t+1} = \\theta_t - \\frac{\\alpha}{\\sqrt{\\hat{v}_t} + \\epsilon} \\hat{m}_t$\n\n"
        "⚠️ **Top Exam Traps & Misconceptions:**\n"
        "1. *Trap:* Confusing moment bias correction with learning rate schedules. (Bias correction only fixes $m_0=0$ startup bias!).\n"
        "2. *Trap:* Thinking Adam replaces SGD in all vision tasks. (SGD+M often matches or outperforms Adam on ResNet generalization!).\n\n"
        "🎯 **Standard Hyperparameters:** $\\alpha=10^{-3}, \\beta_1=0.9, \\beta_2=0.999, \\epsilon=10^{-8}$."
    ),
    "topic-3": (
        "⚡ **High-Yield Exam Cram: MLPs & Backpropagation**\n\n"
        "📌 **Must-Know Formula:**\n"
        "- Sigmoid derivative max: $\\sigma'(z) \\le 0.25$\n"
        "- ReLU derivative: $f'(z) = 1$ for $z > 0$, $0$ for $z < 0$\n\n"
        "⚠️ **Top Exam Traps & Misconceptions:**\n"
        "1. *Trap:* Thinking deep networks with linear activations can learn complex non-linear curves. (FALSE: Compositions of linear functions collapse into a single linear map!).\n"
        "2. *Trap:* Dying ReLU: If a neuron's weights update such that $z < 0$ for all training points, gradient is permanently $0$."
    ),
    "topic-4": (
        "⚡ **High-Yield Exam Cram: CNNs & ResNets**\n\n"
        "📌 **Must-Know Formula:**\n"
        "- Output Dimension: $O = \\lfloor \\frac{W - K + 2P}{S} \\rfloor + 1$\n"
        "- Residual Skip: $\\frac{\\partial L}{\\partial x} = \\frac{\\partial L}{\\partial \\mathcal{H}} (\\frac{\\partial \\mathcal{F}}{\\partial x} + 1)$\n\n"
        "⚠️ **Top Exam Traps & Misconceptions:**\n"
        "1. *Trap:* Stacking two $3\\times 3$ convolutions has a receptive field of $5\\times 5$, but uses $2 \\times 9 = 18$ parameters vs $25$ for a single $5\\times 5$ (28% savings!).\n"
        "2. *Trap:* ResNet skip connections do not add parameters when dimensions match."
    ),
    "topic-5": (
        "⚡ **High-Yield Exam Cram: Sequence Models & LSTMs**\n\n"
        "📌 **Must-Know Formula:**\n"
        "- Forget Gate: $f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)$\n"
        "- Cell State: $C_t = f_t C_{t-1} + i_t \\tilde{C}_t$\n\n"
        "⚠️ **Top Exam Traps & Misconceptions:**\n"
        "1. *Trap:* Confusing the Cell State $C_t$ (linear conveyor belt) with the Hidden State $h_t$ (gated output).\n"
        "2. *Trap:* BPTT (Backpropagation Through Time) is computationally truncated to $k$ steps to prevent memory explosion."
    ),
    "topic-6": (
        "⚡ **High-Yield Exam Cram: Transformers & Attention**\n\n"
        "📌 **Must-Know Formula:**\n"
        "- Attention: $\\text{Softmax}(\\frac{Q K^T}{\\sqrt{d_k}}) V$\n"
        "- Complexity: $O(N^2 d)$ with respect to sequence length $N$\n\n"
        "⚠️ **Top Exam Traps & Misconceptions:**\n"
        "1. *Trap:* Forgetting why Positional Encodings are required (Self-attention is permutation-equivariant; word order is invisible without them!).\n"
        "2. *Trap:* Thinking multi-head attention increases total parameters (Dimension is split: $d_k = d_{model} / h$)."
    )
}

class GroundedTutor:
    """The core conversational study companion with multi-persona pedagogical intelligence."""

    def __init__(self, course: Course, retriever: HybridRetriever, learner_model: LearnerModel):
        self.course = course
        self.retriever = retriever
        self.learner_model = learner_model
        self.citation_engine = CitationEngine()

    async def answer_query(
        self,
        query: str,
        bilingual_mode: bool = False,
        persona: str = "professor",
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes student query with hybrid retrieval, grounding verification,
        applies pedagogical persona framing, and generates response with interactive citations.
        """
        # 1. Retrieve top source units
        retrieved = self.retriever.retrieve(query, top_k=3)
        
        # 2. Verify grounding & refusal policy
        verif = GroundingVerifier.check_query_grounding(query, retrieved)
        
        if not verif["is_grounded"]:
            # Query is declined strictly
            return {
                "query": query,
                "status": verif["status"],
                "is_grounded": False,
                "confidence": verif["confidence"],
                "answer": verif["refusal_message"],
                "citations": [],
                "modal_data": [],
                "bilingual": bilingual_mode,
                "persona": persona,
                "updated_mastery": self.learner_model.get_all_mastery()
            }

        top_units = [u[0] for u in retrieved]
        top_unit = top_units[0]
        
        # Prepare citation modal data for frontend
        modal_payloads = [self.citation_engine.build_citation_modal_data(u) for u in top_units]
        citation_chips = [f"[{u.citation_label}]" for u in top_units]

        # 3. Call Generative AI Engine (Gemini / Multimodal)
        context_str = "\n\n".join([
            f"Source: {u.citation_label}\nContent: {u.text_content}\nVisuals: {u.visual_description or 'None'}"
            for u in top_units
        ])
        answer_text = await AIService.generate_grounded_answer(
            query=query,
            context_str=context_str,
            persona=persona,
            bilingual_mode=bilingual_mode,
            api_key_override=api_key_override
        ) or ""

        # 4. Built-in Local Multi-Persona Synthesis Engine (if no API key or API call failed)
        if not answer_text:
            persona_key = persona.lower()
            topic_id = top_unit.topic_id

            if bilingual_mode or persona_key == "hinglish":
                hinglish_body = BilingualEngine.get_hinglish_explanation(top_unit.topic_id, top_unit.text_content)
                answer_text = (
                    f"{hinglish_body}\n\n"
                    f"**Course Citations:**\n"
                    f"- {top_unit.citation_label}: {top_unit.text_content[:280]}...\n\n"
                    f"*Click any citation badge below to inspect original video, textbook, or slide sources.*"
                )
            elif persona_key == "feynman":
                analogy = FEYNMAN_ANALOGIES.get(topic_id, (
                    f"💡 **Feynman Intuition:** Imagine this concept like a physical pulley system: {top_unit.text_content[:200]}..."
                ))
                answer_text = (
                    f"{analogy}\n\n"
                    f"**Academic Foundation ({top_unit.citation_label}):**\n"
                    f"> {top_unit.text_content}\n\n"
                )
                if top_unit.visual_description:
                    answer_text += f"**Visual Diagram Insight:**\n> {top_unit.visual_description}\n\n"
                answer_text += f"*Grounding Reference: [{top_unit.citation_label}] ({top_unit.topic_name})*"

            elif persona_key == "socratic":
                socratic_body = SOCRATIC_HINTS.get(topic_id, (
                    "🏛️ **Socratic Guided Inquiry:**\n"
                    "Consider the core question from first principles:\n"
                    f"1. How does the concept in **{top_unit.citation_label}** operate when inputs approach boundary values?\n"
                    "2. What behavior does the mathematical objective penalize most severely?\n"
                    f"👉 *Examine the excerpt in [{top_unit.citation_label}] to deduce the complete answer!*"
                ))
                answer_text = (
                    f"{socratic_body}\n\n"
                    f"**Relevant Source Excerpt ({top_unit.citation_label}):**\n"
                    f"> {top_unit.text_content[:260]}...\n"
                )

            elif persona_key == "cram":
                cram_body = EXAM_CRAM_SUMMARIES.get(topic_id, (
                    f"⚡ **High-Yield Exam Cram: {top_unit.topic_name}**\n\n"
                    f"📌 **Core Concept:** {top_unit.text_content[:250]}...\n\n"
                    f"🎯 **Cited Source:** {top_unit.citation_label}"
                ))
                answer_text = f"{cram_body}\n\n*Click the citation badge below to view textbook & lecture proofs.*"

            else:
                # Default "professor" persona
                answer_text = (
                    f"Based on **{top_unit.citation_label}** ({top_unit.topic_name}):\n\n"
                    f"{top_unit.text_content}\n\n"
                )
                if top_unit.equations:
                    answer_text += "**Mathematical Formulation:**\n"
                    for eq in top_unit.equations:
                        answer_text += f"- ${eq}$\n"
                    answer_text += "\n"
                    
                if top_unit.visual_description:
                    answer_text += f"**Visual Diagram Insight:**\n> {top_unit.visual_description}\n\n"
                    
                if len(top_units) > 1:
                    second_unit = top_units[1]
                    answer_text += f"**Cross-Source Grounding ({second_unit.citation_label}):**\n{second_unit.text_content[:220]}...\n"

        # 5. Update BKT learner model from conversational interaction
        self.learner_model.record_quiz_answer(top_unit.topic_id, top_unit.topic_name, is_correct=True)

        return {
            "query": query,
            "status": verif["status"],
            "is_grounded": True,
            "confidence": verif["confidence"],
            "answer": answer_text,
            "citations": citation_chips,
            "modal_data": modal_payloads,
            "bilingual": bilingual_mode,
            "persona": persona,
            "primary_topic": top_unit.topic_name,
            "updated_mastery": self.learner_model.get_all_mastery()
        }
