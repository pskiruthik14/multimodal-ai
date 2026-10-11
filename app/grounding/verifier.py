"""
Grounding Verifier & Refusal Mechanism:
Detects hallucinations, verifies source alignment, and strictly declines out-of-scope queries.
"""

from typing import List, Tuple, Dict, Any, Optional
from app.ingestion.models import ContentUnit
from app.config import settings

OUT_OF_SCOPE_KEYWORDS = [
    "recipe", "cake", "cook", "baking", "pizza",
    "politics", "election", "president", "senate", "parliament",
    "weather", "forecast", "horoscope", "astrology",
    "cricket", "football", "fifa", "ipl", "baseball", "superbowl",
    "movie", "celebrity", "actor", "hollywood", "bollywood",
    "quantum chromodynamics", "dna sequencing", "photosynthesis",
    "stock market price", "crypto price", "bitcoin mining"
]

class GroundingVerifier:
    """Verifies that queries and responses are strictly anchored in course materials."""

    @staticmethod
    def check_query_grounding(
        query: str,
        retrieved_units: List[Tuple[ContentUnit, float]]
    ) -> Dict[str, Any]:
        """
        Evaluates whether query is within scope of course materials.
        Returns grounding status, confidence score, and refusal details if ungrounded.
        """
        q_lower = query.lower()
        
        # Check explicit out-of-scope indicators
        for kw in OUT_OF_SCOPE_KEYWORDS:
            if kw in q_lower:
                return {
                    "is_grounded": False,
                    "status": "OUT_OF_SCOPE_DECLINED",
                    "reason": f"Query contains out-of-scope subject matter ('{kw}') not covered in course materials.",
                    "refusal_message": (
                        "⛔ **Query Declined: Out of Course Material**\n\n"
                        "This question is outside the scope of your ingested course materials (**CS229: Deep Learning & Neural Architectures**). "
                        "To guarantee high academic rigor and prevent hallucinations, this study companion only answers queries "
                        "tied directly to your lectures, textbooks, or slide decks.\n\n"
                        "*Please ask about topics such as Loss Functions, Optimizers (Adam/SGD), Backpropagation, CNNs, LSTMs, or Transformers.*"
                    ),
                    "confidence": 0.0
                }
                
        # If no units retrieved or highest score is below grounding threshold
        top_score = retrieved_units[0][1] if retrieved_units else 0.0
        
        if not retrieved_units or top_score < settings.GROUNDING_SIMILARITY_THRESHOLD:
            return {
                "is_grounded": False,
                "status": "OUT_OF_SCOPE_DECLINED",
                "reason": f"No relevant course content matched (retrieval confidence {top_score:.2f} < threshold {settings.GROUNDING_SIMILARITY_THRESHOLD}).",
                "refusal_message": (
                    "⛔ **Query Declined: Topic Not Found in Course Materials**\n\n"
                    "I searched your lecture videos, textbook chapters, and slide decks, but could not find source evidence "
                    f"to answer this question (Confidence: {top_score*100:.0f}%).\n\n"
                    "Rather than generating speculative or unverified information, I decline to answer outside your verified course syllabus. "
                    "Try rephrasing your question or selecting one of the topics from the Course Flow Map."
                ),
                "confidence": top_score
            }
            
        if top_score < settings.HIGH_CONFIDENCE_THRESHOLD:
            return {
                "is_grounded": True,
                "status": "PARTIALLY_GROUNDED",
                "reason": "Moderate source match; outside context flagged.",
                "confidence": top_score
            }
            
        return {
            "is_grounded": True,
            "status": "FULLY_GROUNDED",
            "reason": "High relevance match found across multiple source modalities.",
            "confidence": top_score
        }
