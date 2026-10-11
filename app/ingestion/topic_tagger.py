"""
Topic Ontology and Concept Prerequisite Graph Engine
Organizes content units into topics, concepts, and prerequisite DAGs.
"""

from typing import List, Dict, Any, Tuple
import networkx as nx
from app.ingestion.models import Topic, ContentUnit, Course

class KnowledgeGraphManager:
    """Manages the topic prerequisite Directed Acyclic Graph (DAG) and concept hierarchy."""
    
    def __init__(self, course: Course):
        self.course = course
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Construct the NetworkX DAG from course topics."""
        for topic in self.course.topics:
            self.graph.add_node(
                topic.id,
                name=topic.name,
                description=topic.description,
                order=topic.order,
                key_concepts=topic.key_concepts
            )
            
        for topic in self.course.topics:
            for prereq_id in topic.prerequisites:
                if self.graph.has_node(prereq_id):
                    # Edge from prerequisite -> advanced topic
                    self.graph.add_edge(prereq_id, topic.id)

    def get_prerequisites_for_topic(self, topic_id: str) -> List[str]:
        """Returns direct and ancestral prerequisites for a given topic."""
        if not self.graph.has_node(topic_id):
            return []
        return list(nx.ancestors(self.graph, topic_id))

    def get_learning_path(self) -> List[str]:
        """Returns topologically sorted sequence of topics."""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # Fallback if cycle detected
            return [t.id for t in sorted(self.course.topics, key=lambda x: x.order)]

    def tag_content_unit(self, unit: ContentUnit) -> ContentUnit:
        """Assign best matching topic and concepts to a content unit."""
        best_topic = None
        max_overlap = -1
        unit_text = (unit.title + " " + unit.text_content).lower()
        
        for topic in self.course.topics:
            score = 0
            # Topic name match
            if topic.name.lower() in unit_text:
                score += 5
            # Key concepts match
            for concept in topic.key_concepts:
                if concept.lower() in unit_text:
                    score += 3
            if score > max_overlap:
                max_overlap = score
                best_topic = topic
                
        if best_topic and max_overlap > 0:
            unit.topic_id = best_topic.id
            unit.topic_name = best_topic.name
            matched_concepts = [c for c in best_topic.key_concepts if c.lower() in unit_text]
            if matched_concepts:
                unit.concept_tags = list(set(unit.concept_tags + matched_concepts))
        return unit

    def get_graph_export(self, mastery_map: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Exports nodes and edges for front-end visual course flow map / Canvas visualization.
        Mastery map maps topic_id -> float mastery in [0.0, 1.0].
        """
        mastery_map = mastery_map or {}
        nodes = []
        edges = []
        
        # Position nodes in topological rank columns
        levels = {}
        for node in nx.topological_sort(self.graph):
            preds = list(self.graph.predecessors(node))
            levels[node] = 0 if not preds else max(levels[p] for p in preds) + 1
            
        level_counts = {}
        for node, lvl in levels.items():
            level_counts[lvl] = level_counts.get(lvl, 0) + 1
            
        current_y_indices = {}
        for node in self.graph.nodes():
            lvl = levels.get(node, 0)
            idx = current_y_indices.get(lvl, 0)
            current_y_indices[lvl] = idx + 1
            total_in_col = level_counts[lvl]
            
            x = 80 + lvl * 180
            y = 70 + (idx - (total_in_col - 1) / 2.0) * 110 + 100
            
            topic_obj = next((t for t in self.course.topics if t.id == node), None)
            mastery = mastery_map.get(node, 0.20)
            
            nodes.append({
                "id": node,
                "label": topic_obj.name if topic_obj else node,
                "description": topic_obj.description if topic_obj else "",
                "key_concepts": topic_obj.key_concepts if topic_obj else [],
                "order": topic_obj.order if topic_obj else 0,
                "x": x,
                "y": y,
                "mastery": round(mastery, 2),
                "status": "mastered" if mastery >= 0.85 else ("developing" if mastery >= 0.50 else "learning")
            })
            
        for u, v in self.graph.edges():
            edges.append({
                "from": u,
                "to": v,
                "source": u,
                "target": v
            })
            
        return {
            "nodes": nodes,
            "edges": edges,
            "total_topics": len(nodes)
        }
