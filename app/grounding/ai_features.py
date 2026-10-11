"""
Advanced AI Features Engine for SynapseLearn AI:
- AI Misconception Remediation Clinic
- AI Multimodal Diagram & Architecture Explainer
- AI Concept Comparator & Trade-off Matrix
- AI Dynamic Flashcard Synthesis
"""

from typing import Dict, Any, List, Optional
import httpx
from app.ingestion.models import Course, ContentUnit
from app.services.ai_service import AIService
from app.config import settings

class AIMisconceptionClinic:
    """Provides targeted cognitive remediation for diagnosed student misconceptions."""

    REMEDIATION_KNOWLEDGE_BASE = {
        "Memory misconception": {
            "title": "Loss Function Memory vs Saturation",
            "explanation": (
                "You associated Cross-Entropy with GPU memory efficiency. In reality, memory usage for backpropagation "
                "depends on tensor dimensions and batch size, not the loss function formulation. The true mathematical "
                "reason Cross-Entropy is mandatory with Softmax is **gradient saturation**:\n\n"
                "When MSE is used with Softmax, the gradient $\\frac{\\partial L}{\\partial z}$ contains the derivative "
                "$\\sigma'(z) = \\sigma(z)(1 - \\sigma(z))$. If the network is confidently incorrect (e.g. predicting $p \\approx 0.001$ "
                "when $y = 1$), $\\sigma'(z) \\to 0$, causing gradient vanishing and halting learning. Cross-Entropy's logarithm "
                "perfectly cancels this term, leaving a clean linear error $\\frac{\\partial L}{\\partial z} = p - y$."
            ),
            "key_takeaway": "Cross-Entropy cures gradient saturation, not memory bottlenecks.",
            "citation": "Slide Deck 1, Slide 7 / Lecture 1 @ 06:15",
            "practice_check": {
                "question": "If a network outputs $p = 0.01$ for true label $y = 1$, what is the Cross-Entropy error signal $\\frac{\\partial L}{\\partial z}$?",
                "options": ["A) -0.99 (Strong gradient)", "B) ~0.00 (Vanished gradient)", "C) Undefined"],
                "correct": "A",
                "explanation": "Since $\\frac{\\partial L}{\\partial z} = p - y = 0.01 - 1 = -0.99$, a massive gradient flows back to swiftly correct the weights!"
            }
        },
        "Convexity misconception": {
            "title": "Convexity vs Neural Network Non-Convexity",
            "explanation": (
                "You noted that Cross-Entropy makes the loss surface convex. While Cross-Entropy is strictly convex with respect to "
                "linear model parameters (like in logistic regression), **deep multi-layer neural networks are inherently non-convex** "
                "regardless of the loss function chosen! Non-linear activations ($ReLU, \\tanh, \\sigma$) and parameter permutations "
                "create high-dimensional landscapes filled with saddle points, ravines, and local minima."
            ),
            "key_takeaway": "Loss functions cannot override the non-convex geometry induced by hidden layer compositions.",
            "citation": "Textbook Ch 1, p. 18",
            "practice_check": {
                "question": "What mathematical object dictates the local curvature and ill-conditioning in non-convex loss surfaces?",
                "options": ["A) The Hessian matrix $H = \\nabla^2 L$", "B) The Jacobian of the input data", "C) The Softmax temperature"],
                "correct": "A",
                "explanation": "The Hessian matrix contains second-order partial derivatives. Its condition number $\\kappa = \\lambda_{\\max} / \\lambda_{\\min}$ governs how severely the landscape resembles an elongated ravine."
            }
        },
        "Decay schedule confusion": {
            "title": "Moment Bias Correction vs Learning Rate Decay",
            "explanation": (
                "You conflated Adam's moment bias correction with learning rate schedules. A learning rate decay schedule "
                "(such as Cosine Annealing or Step Decay) reduces the global learning rate $\\alpha_t$ over training epochs. "
                "In contrast, Adam's bias correction $\\hat{m}_t = \\frac{m_t}{1 - \\beta_1^t}$ and $\\hat{v}_t = \\frac{v_t}{1 - \\beta_2^t}$ "
                "specifically corrects the statistical bias caused by initializing moment accumulators $m_0 = 0$ and $v_0 = 0$."
            ),
            "key_takeaway": "Bias correction acts on early step initialization, whereas decay schedules act across global epochs.",
            "citation": "Textbook Ch 2, p. 45",
            "practice_check": {
                "question": "As iteration step $t \\to \\infty$, what happens to the bias correction term $(1 - \\beta^t)$?",
                "options": ["A) It approaches 1.0, so the correction naturally phases out", "B) It approaches 0, magnifying the gradients", "C) It oscillates with $\\beta$"],
                "correct": "A",
                "explanation": "Since $\\beta < 1$, $\\beta^t \\to 0$, which makes $(1 - \\beta^t) \\to 1$. Hence, bias correction is only active during the initial iterations!"
            }
        },
        "default": {
            "title": "Targeted Concept Misconception Remediation",
            "explanation": (
                "Conceptual slip detected: In deep learning optimization and architectures, subtle differences in gradient flow, "
                "initialization scaling, and dimensional preservation have profound consequences on convergence."
            ),
            "key_takeaway": "Carefully trace how derivatives propagate across layers via the chain rule.",
            "citation": "Course Syllabus: CS229 Foundations",
            "practice_check": {
                "question": "What is the primary mechanism to diagnose gradient issues in deep networks?",
                "options": ["A) Inspecting gradient norms layer-by-layer during backward passes", "B) Increasing batch size to infinity", "C) Removing all activation functions"],
                "correct": "A",
                "explanation": "Tracking gradient norms reveals whether gradients are vanishing (approaching 0) or exploding (becoming NaN/infinite)."
            }
        }
    }

    @classmethod
    async def remediate(
        cls,
        misconception_text: str,
        topic_name: str,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates interactive diagnostic coaching for a student misconception."""
        # 1. Attempt Generative AI remediation via AIService
        ai_res = await AIService.remediate_misconception(
            misconception_text=misconception_text,
            topic_name=topic_name,
            api_key_override=api_key_override
        )
        if ai_res and isinstance(ai_res, dict):
            practice = ai_res.get("practice_check", {})
            return {
                "title": ai_res.get("title", f"Remediation: {topic_name}"),
                "explanation": ai_res.get("explanation", ""),
                "key_takeaway": ai_res.get("key_takeaway", ""),
                "citation": ai_res.get("citation", f"CS229 Grounding • {topic_name}"),
                "practice_check": {
                    "question": practice.get("question", ai_res.get("practice_question", "")),
                    "options": practice.get("options", ai_res.get("practice_options", [])),
                    "correct": practice.get("correct", ai_res.get("practice_correct", "A")),
                    "explanation": practice.get("explanation", ai_res.get("practice_explanation", ""))
                }
            }

        # 2. Local Heuristic Engine
        matched_key = "default"
        for k in cls.REMEDIATION_KNOWLEDGE_BASE:
            if k.lower() in misconception_text.lower():
                matched_key = k
                break
        
        rem_data = cls.REMEDIATION_KNOWLEDGE_BASE[matched_key].copy()
        if matched_key == "default":
            rem_data["title"] = f"Remediation: {topic_name}"
            rem_data["explanation"] = f"**Diagnosed Pitfall:** {misconception_text}\n\n" + rem_data["explanation"]
        return rem_data


class AIDiagramExplainer:
    """Multimodal vision and diagram explainer for deep learning figures."""

    DIAGRAM_ANALYSES = {
        "unit-tb-01": {
            "title": "Figure 1.4: Ill-Conditioned Quadratic Bowl & Gradient Oscillations",
            "architecture_type": "Optimization Landscape Contour",
            "visual_elements": [
                "**Concentric Ellipses (Purple & Indigo):** Represent level sets (isocontours) of constant loss $L(w_1, w_2)$. The elongated shape indicates high condition number $\\kappa = \\lambda_{\\max} / \\lambda_{\\min} \\gg 1$.",
                "**Steep Canyon Walls:** Along the minor axis (steep vertical direction), gradients are large, causing standard SGD to bounce violently between the walls.",
                "**Gentle Ravine Floor:** Along the major axis (horizontal direction towards the minimum), gradients are tiny, resulting in slow progress.",
                "**Red Dashed Trajectory:** Demonstrates high-frequency oscillation of un-momentumized Gradient Descent, wasting computational steps bouncing perpendicularly."
            ],
            "mathematical_takeaway": "Adding Polyak Momentum cancels the oscillating vertical components while accumulating velocity horizontally: $v_t = \\beta v_{t-1} + (1-\\beta) g_t$.",
            "citation": "Textbook Ch 1, p. 18 (Figure 1.4)"
        },
        "unit-sl-02": {
            "title": "Slide 14: Adam Bias Correction Curve",
            "architecture_type": "Statistical Estimator Trajectory",
            "visual_elements": [
                "**Dashed Red Line ($m_t$ uncorrected):** Starts near zero because $m_0 = 0$. With $\\beta_1 = 0.9$, even strong gradients take multiple steps to pull the average away from zero.",
                "**Solid Green Line ($\\hat{m}_t$ bias-corrected):** Instantly matches the expected gradient magnitude from step $t=1$ by scaling with $\\frac{1}{1 - \\beta_1^t}$.",
                "**Convergence Horizon:** As $t \\to 50$, both curves merge smoothly as $\\beta_1^t \\to 0$."
            ],
            "mathematical_takeaway": "Bias correction ensures stable early step sizes without requiring manual learning rate warm-up tricks.",
            "citation": "Slide Deck 1, Slide 14"
        },
        "unit-sl-04": {
            "title": "Slide 8: ResNet Residual Block with Identity Shortcut",
            "architecture_type": "Deep Convolutional Residual Block",
            "visual_elements": [
                "**Weight Layers (3x3 Convolutions):** Compute the residual mapping $\\mathcal{F}(x)$.",
                "**Curved Identity Shortcut Arrow ($+x$):** Bypasses the two convolutions, routing the input directly to the post-activation addition node.",
                "**Element-wise Addition ($\\oplus$):** Synthesizes output $\\mathcal{H}(x) = \\mathcal{F}(x) + x$ before the final ReLU non-linearity.",
                "**Backward Gradient Flow:** During backpropagation, $\\frac{\\partial L}{\\partial x} = \\frac{\\partial L}{\\partial \\mathcal{H}} (\\frac{\\partial \\mathcal{F}}{\\partial x} + 1)$. The '+1' term guarantees that gradients flow backwards unattenuated!"
            ],
            "mathematical_takeaway": "The additive identity connection acts as a gradient superhighway, eliminating vanishing gradients in networks with 100+ to 1000+ layers.",
            "citation": "Slide Deck 3, Slide 8 / Textbook Ch 4, p. 102"
        },
        "unit-tb-06": {
            "title": "Figure 6.1: Scaled Dot-Product & Multi-Head Attention",
            "architecture_type": "Transformer Attention Block",
            "visual_elements": [
                "**Linear Projections ($Q, K, V$):** Map input tokens into Query, Key, and Value subspaces of dimension $d_k, d_k, d_v$.",
                "**MatMul ($Q K^T$):** Calculates pairwise token similarity compatibility matrix.",
                "**Scale Factor ($\\frac{1}{\\sqrt{d_k}}$):** Divides dot products to prevent softmax argument variance from growing with $d_k$.",
                "**Softmax Node:** Generates normalized probability weights across input sequence positions.",
                "**Weighted Value Aggregation:** Multiplies softmax probabilities by Value vectors $V$ to compute context-aware representations."
            ],
            "mathematical_takeaway": "Scaled dot-product attention has $O(N^2)$ sequence complexity and is permutation-equivariant, requiring positional encodings for word ordering.",
            "citation": "Textbook Ch 6, p. 154 (Figure 6.1)"
        }
    }

    @classmethod
    def explain_diagram(cls, unit_id: str) -> Dict[str, Any]:
        """Provides deep structural diagram analysis for visual figures."""
        if unit_id in cls.DIAGRAM_ANALYSES:
            return cls.DIAGRAM_ANALYSES[unit_id]
            
        # Default analysis for any unit with visual diagram
        return {
            "title": "Course Technical Figure Analysis",
            "architecture_type": "Deep Learning Architectural Schematic",
            "visual_elements": [
                "**Input Vector Flow:** Data flows forward through parameterized transformations.",
                "**Mathematical Operator Nodes:** Highlight point-wise non-linearities and normalization steps.",
                "**Residual / Feedback Pathways:** Depict backpropagation gradient pathways and skip connections."
            ],
            "mathematical_takeaway": "Grounding diagrams in mathematical formulations prevents misinterpretation of vector dimensionalities.",
            "citation": "CS229 Multimodal Technical Figures"
        }

    @classmethod
    async def explain_diagram_ai(
        cls,
        unit_id: str,
        content_unit: Optional[ContentUnit] = None,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provides dynamic Generative AI diagram analysis using Gemini for any figure or content unit."""
        if content_unit and (content_unit.visual_description or content_unit.equations):
            ai_res = await AIService.explain_diagram(
                diagram_title=content_unit.title,
                visual_description=content_unit.visual_description or content_unit.text_content,
                equations=content_unit.equations or [],
                citation=content_unit.citation_label,
                api_key_override=api_key_override
            )
            if ai_res and isinstance(ai_res, dict):
                return ai_res

        return cls.explain_diagram(unit_id)


class AIConceptComparator:
    """Generates side-by-side architectural and algorithm trade-off comparison matrices."""

    COMPARISON_TOPICS = {
        "optimizers": {
            "title": "Deep Learning Optimizers: SGD vs Momentum vs RMSProp vs Adam",
            "headers": ["Optimizer", "Update Rule Mechanism", "Strengths", "Weaknesses / Gotchas", "Best Use Case"],
            "rows": [
                [
                    "Standard SGD",
                    "$\\theta_{t+1} = \\theta_t - \\alpha g_t$",
                    "Simple, low memory footprint, good generalization",
                    "Oscillates in ill-conditioned ravines; stalls at saddle points",
                    "Small models, fine-tuning convex layers"
                ],
                [
                    "Polyak Momentum",
                    "$v_t = \\beta v_{t-1} + (1-\\beta) g_t$",
                    "Accelerates along consistent directions, dampens oscillations",
                    "Can overshoot narrow minima; requires tuning $\\beta$",
                    "Computer vision (ResNets), standard SGD+M baselines"
                ],
                [
                    "RMSProp",
                    "$v_t = \\beta_2 v_{t-1} + (1-\\beta_2) g_t^2$",
                    "Adapts learning rate per-parameter by dividing by $\\sqrt{v_t}$",
                    "Can be sensitive to initial learning rate $\\alpha$",
                    "RNNs, sequence models, non-stationary objectives"
                ],
                [
                    "Adam",
                    "Combines Momentum ($\\hat{m}_t$) and RMSProp ($\\hat{v}_t$) with bias correction",
                    "Fast initial convergence, robust to default hyperparameters",
                    "May generalize slightly worse than SGD+M; weight decay needs AdamW",
                    "Transformers, LLMs, complex multi-modal networks"
                ]
            ],
            "citations": ["Lecture 1 @ 21:40", "Textbook Ch 2, p. 45", "Slide Deck 1, Slide 14"]
        },
        "losses": {
            "title": "Classification Loss Functions: MSE vs Cross-Entropy",
            "headers": ["Property", "Mean Squared Error (MSE)", "Cross-Entropy Loss (CE)", "Architectural Impact"],
            "rows": [
                [
                    "Formulation",
                    "$\\frac{1}{2} (y - \\hat{y})^2$",
                    "$- [y \\ln(\\hat{y}) + (1-y) \\ln(1-\\hat{y})]$",
                    "CE measures statistical Kullback-Leibler divergence"
                ],
                [
                    "Gradient with Sigmoid/Softmax",
                    "$(\\hat{y} - y) \\cdot \\sigma'(z)$",
                    "$\\hat{y} - y$",
                    "CE cancels the derivative $\\sigma'(z)$, preventing saturation"
                ],
                [
                    "Confidently Wrong Gradient",
                    "$\\to 0$ (gradient vanishes)",
                    "$\\to 1$ (steep corrective gradient)",
                    "MSE halts learning when model is wrong; CE rapidly corrects it"
                ],
                [
                    "Convexity with Linear Model",
                    "Non-convex with sigmoid",
                    "Strictly convex",
                    "CE guarantees unique global optimum for linear logistic regression"
                ]
            ],
            "citations": ["Lecture 1 @ 06:15", "Slide Deck 1, Slide 7"]
        },
        "architectures": {
            "title": "Sequence Architectures: Vanilla RNN vs LSTM vs Transformer",
            "headers": ["Architecture", "Temporal Processing", "Memory Horizon", "Computational Complexity", "Key Bottleneck"],
            "rows": [
                [
                    "Vanilla RNN",
                    "Sequential $h_t = \\tanh(W_{hh} h_{t-1} + W_{xh} x_t)$",
                    "Short (10-20 steps)",
                    "$O(N \\cdot d^2)$ sequential",
                    "Exponential vanishing/exploding gradients through time"
                ],
                [
                    "LSTM",
                    "Sequential with gating (Forget, Input, Output) & Cell State $C_t$",
                    "Moderate (100-300 steps)",
                    "$O(N \\cdot d^2)$ sequential",
                    "Sequential bottleneck prevents GPU parallelization across time"
                ],
                [
                    "Transformer",
                    "Non-sequential, full pairwise Self-Attention with Positional Encodings",
                    "Long (thousands to millions of tokens)",
                    "$O(N^2 \\cdot d)$ parallelizable",
                    "Quadratic memory complexity with sequence length $N$"
                ]
            ],
            "citations": ["Textbook Ch 5, p. 128", "Lecture 4 @ 29:15", "Textbook Ch 6, p. 154"]
        }
    }

    @classmethod
    def get_comparison(cls, comparison_key: str) -> Dict[str, Any]:
        """Returns comparison matrix for given key."""
        key = comparison_key.lower()
        if "loss" in key or "mse" in key or "entropy" in key:
            return cls.COMPARISON_TOPICS["losses"]
        elif "arch" in key or "rnn" in key or "lstm" in key or "transformer" in key or "sequence" in key:
            return cls.COMPARISON_TOPICS["architectures"]
        return cls.COMPARISON_TOPICS["optimizers"]

    @classmethod
    async def compare_concepts_ai(
        cls,
        comparison_key: str,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dynamically generates comprehensive trade-off matrix for ANY concept query via Generative AI."""
        ai_res = await AIService.compare_concepts(
            comparison_query=comparison_key,
            api_key_override=api_key_override
        )
        if ai_res and isinstance(ai_res, dict) and "headers" in ai_res and "rows" in ai_res:
            return ai_res

        return cls.get_comparison(comparison_key)
