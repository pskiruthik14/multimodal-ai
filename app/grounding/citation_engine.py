"""
Citation Engine: Formats grounded responses with interactive citation links
and structured modal payloads for deep-linking (video timestamp, slide preview, textbook page).
"""

from typing import List, Dict, Any, Tuple
from app.ingestion.models import ContentUnit, SourceType

class CitationEngine:
    """Manages deep-linking citations for text, slides, and video playback."""

    @staticmethod
    def format_inline_citations(units: List[ContentUnit]) -> str:
        """Formats citation chips markdown."""
        chips = []
        for u in units:
            chips.append(f"[{u.citation_label}](#cite-{u.id})")
        return " ".join(chips)

    @staticmethod
    def build_citation_modal_data(unit: ContentUnit) -> Dict[str, Any]:
        """Builds exact payload to open in frontend media viewer modal."""
        payload = {
            "id": unit.id,
            "title": unit.title,
            "source_type": unit.source_type.value,
            "source_name": unit.source_name,
            "citation_label": unit.citation_label,
            "topic_name": unit.topic_name,
            "text_content": unit.text_content,
            "equations": unit.equations,
            "visual_description": unit.visual_description,
            "diagram_svg": unit.diagram_svg
        }
        
        if unit.source_type == SourceType.VIDEO:
            payload["video_start_s"] = unit.timestamp_start_s
            payload["video_end_s"] = unit.timestamp_end_s
            payload["timestamp_formatted"] = unit.timestamp_formatted
            payload["video_embed_url"] = unit.video_embed_url
            
        elif unit.source_type == SourceType.TEXTBOOK:
            payload["page_number"] = unit.page_number
            
        elif unit.source_type == SourceType.SLIDE:
            payload["slide_number"] = unit.slide_number
            
        return payload
