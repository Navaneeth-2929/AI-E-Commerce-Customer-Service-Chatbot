import uuid
from copy import deepcopy


class SessionService:
    def __init__(self):
        self.sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str | None) -> tuple[str, dict]:
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id]

        new_session_id = session_id or str(uuid.uuid4())
        session = {
            "user_name": None,
            "order_id": None,
            "product_name": None,
            "selected_category": None,
            "selected_subcategory": None,
            "selected_brand": None,
            "selected_item": None,
            "previous_intent": None,
            "sentiment": "neutral",
            "negative_count": 0,
        }
        self.sessions[new_session_id] = session
        return new_session_id, session

    def update(self, session_id: str, updates: dict) -> dict:
        self.sessions[session_id].update(updates)
        return deepcopy(self.sessions[session_id])
