"""
Ebbinghaus Spaced Repetition & Forgetting Curve Model
Tracks memory retention decay and schedules optimal revision sessions.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Any, List

class ForgettingCurveTracker:
    """Calculates Ebbinghaus retention and generates spaced repetition review alerts."""

    def __init__(self):
        # Maps topic_id -> dict with last_review_days_ago, review_count, stability_s
        self.topic_schedules: Dict[str, Dict[str, Any]] = {
            "topic-1": {"last_studied_days": 5, "review_count": 2, "stability": 4.0},
            "topic-2": {"last_studied_days": 3, "review_count": 2, "stability": 3.5},
            "topic-3": {"last_studied_days": 1, "review_count": 1, "stability": 2.0},
            "topic-4": {"last_studied_days": 8, "review_count": 1, "stability": 1.5},
            "topic-5": {"last_studied_days": 2, "review_count": 1, "stability": 2.0},
            "topic-6": {"last_studied_days": 0, "review_count": 1, "stability": 2.5}
        }

    def get_retention(self, topic_id: str) -> float:
        """
        Calculates current retention probability:
        R(t) = exp(-delta_t / S)
        """
        info = self.topic_schedules.get(topic_id, {"last_studied_days": 0, "stability": 2.0})
        delta_t = info["last_studied_days"]
        stability = max(1.0, info["stability"])
        r = math.exp(-delta_t / stability)
        return round(r, 2)

    def record_review(self, topic_id: str, success: bool = True):
        """Updates stability and resets elapsed days upon review."""
        if topic_id not in self.topic_schedules:
            self.topic_schedules[topic_id] = {"last_studied_days": 0, "review_count": 0, "stability": 2.0}
            
        cur = self.topic_schedules[topic_id]
        cur["last_studied_days"] = 0
        if success:
            cur["review_count"] += 1
            # Expand stability factor (Leitner-style multiplier)
            cur["stability"] = round(cur["stability"] * 1.8, 1)
        else:
            # Drop stability on lapse
            cur["stability"] = max(1.5, cur["stability"] * 0.7)

    def get_revision_schedule(self) -> List[Dict[str, Any]]:
        """Generates list of topics sorted by urgency of review."""
        items = []
        for tid, data in self.topic_schedules.items():
            retention = self.get_retention(tid)
            urgency = "High (Critical Decay)" if retention < 0.50 else ("Medium (Due Soon)" if retention < 0.75 else "Optimal")
            recommended_in_days = max(0, int(data["stability"] * (1.0 - retention)))
            
            items.append({
                "topic_id": tid,
                "retention": retention,
                "last_studied_days_ago": data["last_studied_days"],
                "review_count": data["review_count"],
                "urgency": urgency,
                "recommended_in_days": recommended_in_days
            })
            
        items.sort(key=lambda x: x["retention"])
        return items
