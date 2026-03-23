import re


class IntentRecognizer:
    def __init__(self, intents: list[dict]):
        self._compiled = []
        for intent in intents:
            patterns = [re.compile(pattern, re.IGNORECASE) for pattern in intent["patterns"]]
            self._compiled.append({"name": intent["name"], "patterns": patterns})

    def detect_intent(self, text: str) -> tuple[str, float]:
        normalized = text.strip()
        best_intent = "fallback"
        best_score = 0.0

        for intent in self._compiled:
            matches = sum(1 for pattern in intent["patterns"] if pattern.search(normalized))
            if not matches:
                continue
            score = min(1.0, 0.4 + (matches * 0.2))
            if score > best_score:
                best_intent = intent["name"]
                best_score = score

        return best_intent, best_score
