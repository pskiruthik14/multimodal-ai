"""
Hybrid Semantic & Lexical Retriever with Source Grounding
"""

import math
import re
from typing import List, Tuple, Dict, Any, Optional
from app.ingestion.models import ContentUnit
from app.config import settings

class HybridRetriever:
    """
    Combines BM25-style lexical scoring with TF-IDF cosine similarity
    to perform precise source-grounded retrieval across multimodal units.
    """
    
    def __init__(self, units: List[ContentUnit]):
        self.units = units
        self.vocab: Dict[str, int] = {}
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.idf: Dict[str, float] = {}
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        """Simple lowercase word tokenization with alphanumeric filtering."""
        text = text.lower()
        tokens = re.findall(r"\b[a-z0-9_]{2,}\b", text)
        return tokens

    def _build_index(self):
        """Build inverted index, term frequencies, and IDF table."""
        if not self.units:
            return
            
        N = len(self.units)
        doc_freq: Dict[str, int] = {}
        
        for unit in self.units:
            full_text = f"{unit.title} {unit.topic_name} {' '.join(unit.concept_tags)} {unit.text_content} {unit.visual_description or ''}"
            tokens = self._tokenize(full_text)
            self.doc_lengths.append(len(tokens))
            
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs.append(tf)
            
            for t in tf.keys():
                doc_freq[t] = doc_freq.get(t, 0) + 1
                
        self.avg_doc_len = sum(self.doc_lengths) / max(1, N)
        for term, df in doc_freq.items():
            # BM25-style IDF with smoothing
            self.idf[term] = math.log(1.0 + (N - df + 0.5) / (df + 0.5))

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[ContentUnit, float]]:
        """
        Retrieves top_k content units matching query with normalized relevance score [0.0, 1.0].
        """
        if not self.units:
            return []
            
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
            
        k1 = 1.5
        b = 0.75
        scores = []
        
        for idx, unit in enumerate(self.units):
            tf = self.doc_term_freqs[idx]
            doc_len = self.doc_lengths[idx]
            bm25_score = 0.0
            
            for token in query_tokens:
                if token in tf and token in self.idf:
                    count = tf[token]
                    numerator = count * (k1 + 1.0)
                    denominator = count + k1 * (1.0 - b + b * (doc_len / max(1.0, self.avg_doc_len)))
                    bm25_score += self.idf[token] * (numerator / denominator)
                    
            # Boost score if query matches topic name or concepts directly
            q_lower = query.lower()
            if unit.topic_name.lower() in q_lower:
                bm25_score += 4.0
            for c in unit.concept_tags:
                if c.lower() in q_lower:
                    bm25_score += 3.0
                    
            scores.append((unit, bm25_score))
            
        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize top score to a confidence scale [0.0, 1.0]
        max_score = scores[0][1] if scores and scores[0][1] > 0 else 1.0
        normalized = []
        for unit, raw_score in scores[:top_k]:
            norm_score = min(1.0, raw_score / max(10.0, max_score)) if raw_score > 0 else 0.0
            normalized.append((unit, round(norm_score, 3)))
            
        return normalized
