"""
Data models for Multimodal Knowledge Base & Content Units
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class SourceType(str, Enum):
    VIDEO = "video"
    TEXTBOOK = "textbook"
    SLIDE = "slide"

class ContentUnit(BaseModel):
    id: str
    course_id: str = "cs229-dl"
    title: str
    source_type: SourceType
    source_name: str
    citation_label: str  # e.g., "Lecture 2 @ 18:45" or "Textbook Ch 3, p. 42"
    timestamp_start_s: Optional[int] = None
    timestamp_end_s: Optional[int] = None
    timestamp_formatted: Optional[str] = None # e.g. "18:45"
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    text_content: str
    visual_description: Optional[str] = None # Information extracted from images/diagrams
    diagram_svg: Optional[str] = None # Visual SVG graphic for modal viewer
    equations: List[str] = Field(default_factory=list)
    topic_id: str
    topic_name: str
    concept_tags: List[str] = Field(default_factory=list)
    video_embed_url: Optional[str] = None

class Topic(BaseModel):
    id: str
    name: str
    description: str
    order: int
    prerequisites: List[str] = Field(default_factory=list) # List of topic_ids
    key_concepts: List[str] = Field(default_factory=list)

class Course(BaseModel):
    id: str
    name: str
    code: str
    description: str
    topics: List[Topic]
    content_units: List[ContentUnit]
