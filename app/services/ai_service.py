"""
Unified Generative AI Engine for SynapseLearn AI:
Provides robust, asynchronous Google Gemini 2.0 / 2.5 integration
with structured JSON schema synthesis, multi-persona prompt engineering,
and intelligent local fallback synthesis for all backend capabilities.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import httpx
from app.config import settings

logger = logging.getLogger("SynapseLearnAI.AIService")

class AIService:
    """
    Central AI Orchestration Service for all multimodal tutoring,
    assessment generation, concept comparison, diagram analysis, and revision workflows.
    """

    @classmethod
    async def call_gemini(
        cls,
        prompt: str,
        system_instruction: Optional[str] = None,
        is_json: bool = False,
        api_key_override: Optional[str] = None,
        model_override: Optional[str] = None,
        timeout: float = 20.0,
        temperature: float = 0.4
    ) -> Optional[Union[str, Dict[str, Any], List[Any]]]:
        """
        Executes an asynchronous call to Google Gemini API (v1beta) using HTTPX.
        Returns extracted text, or parsed JSON if is_json=True.
        """
        api_key = api_key_override or settings.GEMINI_API_KEY
        if not api_key:
            return None

        model = model_override or settings.GEMINI_MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }

        if is_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "").strip()
                            if is_json:
                                try:
                                    # Clean possible markdown wrapping if returned
                                    clean_text = raw_text
                                    if clean_text.startswith("```json"):
                                        clean_text = clean_text[7:]
                                    elif clean_text.startswith("```"):
                                        clean_text = clean_text[3:]
                                    if clean_text.endswith("```"):
                                        clean_text = clean_text[:-3]
                                    return json.loads(clean_text.strip())
                                except Exception as json_err:
                                    logger.warning(f"Failed to parse JSON response: {json_err}. Raw text: {raw_text[:200]}")
                                    return None
                            return raw_text
                else:
                    logger.warning(f"Gemini API returned HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}")

        return None

    @classmethod
    async def generate_grounded_answer(
        cls,
        query: str,
        context_str: str,
        persona: str = "professor",
        bilingual_mode: bool = False,
        api_key_override: Optional[str] = None
    ) -> Optional[str]:
        """Generates source-grounded persona tutor responses."""
        persona_instructions = {
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
        persona_instr = persona_instructions.get(persona.lower(), persona_instructions["professor"])
        
        if bilingual_mode or persona.lower() == "hinglish":
            lang_instr = "Provide explanation in intuitive conversational Hinglish (Hindi + English) with technical English terms."
        else:
            lang_instr = "Provide clear academic explanation in English with LaTeX equations formatted as $math$."

        system_prompt = (
            f"{persona_instr}\n\n"
            "Answer strictly and exclusively using the provided course context excerpts below. "
            "Explicitly cite source locations (e.g. [Lecture 1 @ 06:15] or [Textbook Ch 1, p. 18]). "
            f"{lang_instr}\n"
            "Do NOT hallucinate facts outside the provided context."
        )

        user_prompt = f"Context:\n{context_str}\n\nStudent Question: {query}"
        
        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=False,
            api_key_override=api_key_override,
            temperature=0.3
        )
        return str(res) if res else None

    @classmethod
    async def generate_questions(
        cls,
        topic_name: str,
        difficulty: str = "medium",
        num_questions: int = 3,
        context_str: str = "",
        api_key_override: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Generates dynamic assessment questions complete with distractors and proofs."""
        system_prompt = (
            "You are a Senior Deep Learning & CS Professor designing an adaptive exam. "
            "Generate novel, mathematically rigorous questions strictly matching the given topic and difficulty.\n"
            "You must return a valid JSON array of objects with the exact keys:\n"
            "- question_text: clear problem statement with LaTeX equations ($...$)\n"
            "- type: 'mcq' or 'numerical'\n"
            "- options: array of 4 distinct choices ['A) ...', 'B) ...', 'C) ...', 'D) ...'] if mcq, else empty array\n"
            "- correct_answer: 'A', 'B', 'C', or 'D' (or numerical string like '1.61' if numerical)\n"
            "- solution_explanation: complete step-by-step mathematical derivation\n"
            "- misconception_distractors: map of wrong options to cognitive explanation of why a student made that mistake\n"
            "- citation_label: relevant source citation (e.g. Lecture or Textbook reference)\n"
            "- irt_difficulty_b: float from -2.0 (easy) to +2.0 (hard)\n"
            "- irt_discrimination_a: float from 0.8 to 1.8"
        )

        user_prompt = (
            f"Topic: {topic_name}\n"
            f"Target Difficulty: {difficulty}\n"
            f"Number of Questions: {num_questions}\n"
        )
        if context_str:
            user_prompt += f"\nReference Course Material:\n{context_str}\n"

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.4
        )
        if isinstance(res, list):
            return res
        return None

    @classmethod
    async def remediate_misconception(
        cls,
        misconception_text: str,
        topic_name: str,
        api_key_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Provides targeted AI cognitive remediation for diagnosed student errors."""
        system_prompt = (
            "You are an AI Cognitive Pedagogical Specialist in Deep Learning and Computer Science.\n"
            "A student answered an assessment question incorrectly due to a specific misconception.\n"
            "Return a JSON object with keys:\n"
            "- title: short informative headline (e.g., 'Loss Saturation vs GPU Memory')\n"
            "- explanation: comprehensive 2-3 paragraph explanation contrasting their intuitive misconception with the correct mathematical formulation ($...$)\n"
            "- key_takeaway: one punchy, memorable summary sentence\n"
            "- citation: relevant textbook chapter or lecture citation\n"
            "- practice_check: an interactive 1-question verification object with keys:\n"
            "    * question: problem text\n"
            "    * options: array of 3 options ['A) ...', 'B) ...', 'C) ...']\n"
            "    * correct: 'A', 'B', or 'C'\n"
            "    * explanation: brief proof of why this answer is correct"
        )

        user_prompt = (
            f"Topic: {topic_name}\n"
            f"Diagnosed Student Misconception: {misconception_text}\n"
            "Deconstruct this mental model flaw and generate targeted remediation."
        )

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.3
        )
        if isinstance(res, dict):
            return res
        return None

    @classmethod
    async def explain_diagram(
        cls,
        diagram_title: str,
        visual_description: str,
        equations: List[str] = [],
        citation: str = "",
        api_key_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Generates deep architectural and vector-flow breakdown for technical figures."""
        system_prompt = (
            "You are an AI Multimodal Vision and Neural Architecture Analyst.\n"
            "Given a technical figure or architecture schematic, provide a deep structural breakdown.\n"
            "Return a JSON object with keys:\n"
            "- title: figure title\n"
            "- architecture_type: architecture classification (e.g. 'Transformer Attention Block', 'Optimization Landscape Contour')\n"
            "- visual_elements: array of 3-5 bullet strings explaining data flow, tensor shapes, and component nodes with markdown/math\n"
            "- mathematical_takeaway: 1-2 sentence core theorem or gradient flow insight ($...$)\n"
            "- citation: source citation"
        )

        user_prompt = (
            f"Figure Title: {diagram_title}\n"
            f"Visual Content Description: {visual_description}\n"
            f"Associated Equations: {', '.join(equations) if equations else 'None'}\n"
            f"Citation: {citation}\n"
            "Generate deep structural and vector-flow diagram analysis."
        )

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.3
        )
        if isinstance(res, dict):
            return res
        return None

    @classmethod
    async def compare_concepts(
        cls,
        comparison_query: str,
        api_key_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Dynamically generates comprehensive side-by-side comparison matrix for ANY deep learning concepts."""
        system_prompt = (
            "You are an AI Machine Learning Architect & Benchmark Researcher.\n"
            "Given a comparison query between models, optimizers, architectures, or algorithms, "
            "generate a comprehensive side-by-side trade-off matrix.\n"
            "Return a JSON object with keys:\n"
            "- title: descriptive title of comparison (e.g., 'Modern Optimizers: Adam vs Lion vs Adafactor')\n"
            "- headers: array of 4-5 column headers, e.g. ['Approach', 'Mathematical Formulation', 'Key Strengths', 'Bottlenecks / Failure Modes', 'Ideal Production Use Case']\n"
            "- rows: 2D array of rows, where each row has values corresponding to each header\n"
            "- citations: array of 2-3 standard literature / course citations"
        )

        user_prompt = f"Comparison Query: {comparison_query}\nGenerate structured comparison matrix."

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.3
        )
        if isinstance(res, dict):
            return res
        return None

    @classmethod
    async def generate_flashcards(
        cls,
        topic_name: str,
        num_cards: int = 3,
        context_str: str = "",
        api_key_override: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Synthesizes novel Leitner 5-box spaced repetition flashcards."""
        system_prompt = (
            "You are an AI Learning Engineer designing high-impact Leitner spaced repetition flashcards.\n"
            "Generate novel flashcards testing deep conceptual mechanisms and mathematical definitions.\n"
            "Return a JSON array of objects with keys:\n"
            "- front: clear conceptual prompt or challenging diagnostic question\n"
            "- back: concise, crystal-clear explanation with formulas and intuition\n"
            "- citation: source reference\n"
            "- box: integer 1 to 5 (starting Leitner box)"
        )

        user_prompt = (
            f"Topic: {topic_name}\n"
            f"Number of Flashcards: {num_cards}\n"
        )
        if context_str:
            user_prompt += f"Course Reference:\n{context_str}\n"

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.4
        )
        if isinstance(res, list):
            return res
        return None

    @classmethod
    async def generate_cheat_sheet(
        cls,
        topic_name: str,
        context_str: str = "",
        api_key_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Dynamically generates high-yield exam cheat-sheet for any topic."""
        system_prompt = (
            "You are an expert AI Examiner creating an ultra-dense exam revision cheat-sheet.\n"
            "Return a JSON object with keys:\n"
            "- title: sheet title\n"
            "- key_formulas: array of 3-5 foundational mathematical formulas with LaTeX ($...$)\n"
            "- core_insights: array of 3-5 high-yield conceptual rules, theorems, and exam pitfalls\n"
            "- citations: array of 2-3 course or textbook citations"
        )

        user_prompt = f"Topic: {topic_name}\n"
        if context_str:
            user_prompt += f"Course Content:\n{context_str}\n"

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.3
        )
        if isinstance(res, dict):
            return res
        return None

    @classmethod
    async def generate_audio_brief(
        cls,
        topic_name: str,
        context_str: str = "",
        api_key_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Synthesizes a 2-minute spoken conversational audio brief script."""
        system_prompt = (
            "You are a podcast host and Deep Learning tutor recording a 2-minute Audio Brief.\n"
            "Write an engaging, spoken-word script explaining the topic's core mathematical and architectural intuition.\n"
            "Return a JSON object with keys:\n"
            "- title: audio brief title\n"
            "- duration_est: '2 minutes'\n"
            "- script: natural, spoken-word script (approx 200-250 words)\n"
            "- citations: array of citations referenced"
        )

        user_prompt = f"Topic: {topic_name}\n"
        if context_str:
            user_prompt += f"Reference Excerpts:\n{context_str}\n"

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.4
        )
        if isinstance(res, dict):
            return res
        return None

    @classmethod
    async def generate_study_schedule(
        cls,
        weak_topics: List[str],
        all_topics: List[str],
        days_until_exam: int = 7,
        hours_per_day: float = 2.0,
        api_key_override: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Generates an AI personalized day-by-day exam prep schedule."""
        system_prompt = (
            "You are an AI Academic Coach creating an adaptive spaced-repetition study schedule.\n"
            "Distribute study sessions prioritizing weak topics and balancing revision curves.\n"
            "Return a JSON array of daily plan objects with keys:\n"
            "- day: integer day number (1 to days_until_exam)\n"
            "- primary_topic_id: topic identifier\n"
            "- topic_title: human-readable topic title\n"
            "- allocated_hours: float hours allocated\n"
            "- is_weak_topic: boolean\n"
            "- tasks: array of 3-4 specific actionable revision tasks"
        )

        user_prompt = (
            f"Days until Exam: {days_until_exam}\n"
            f"Daily Study Hours: {hours_per_day}\n"
            f"Diagnosed Weak Topics (Mastery < 60%): {', '.join(weak_topics) if weak_topics else 'None'}\n"
            f"All Topics: {', '.join(all_topics)}\n"
            "Synthesize day-by-day adaptive study plan."
        )

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.3
        )
        if isinstance(res, list):
            return res
        return None

    @classmethod
    async def enrich_uploaded_content(
        cls,
        text_content: str,
        filename: str,
        api_key_override: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Extracts key mathematical formulas, summaries, and topics from uploaded materials."""
        system_prompt = (
            "You are an AI Document Ingestion Engine for CS229.\n"
            "Analyze the provided text excerpt from an uploaded study document.\n"
            "Return a JSON object with keys:\n"
            "- topic_name: primary topic or concept name\n"
            "- summary: concise 2-sentence summary\n"
            "- equations: array of LaTeX formulas found or deduced ($...$)\n"
            "- visual_description: description of any diagram, flow, or graph implied\n"
            "- keywords: array of 4-6 technical keywords"
        )

        user_prompt = f"Filename: {filename}\nExcerpt Content:\n{text_content[:2500]}"

        res = await cls.call_gemini(
            prompt=user_prompt,
            system_instruction=system_prompt,
            is_json=True,
            api_key_override=api_key_override,
            temperature=0.2
        )
        if isinstance(res, dict):
            return res
        return None
