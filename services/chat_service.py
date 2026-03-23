import json
import logging
from pathlib import Path

from nlp.entity_extractor import extract_entities
from nlp.intent_recognizer import IntentRecognizer
from nlp.sentiment import SentimentAnalyzer


LOGGER = logging.getLogger(__name__)


class ChatService:
    def __init__(self, intents_path: Path, responses_path: Path, catalog_path: Path, order_service, session_service):
        with Path(intents_path).open("r", encoding="utf-8") as handle:
            intent_config = json.load(handle)
        with Path(responses_path).open("r", encoding="utf-8") as handle:
            self.responses = json.load(handle)
        with Path(catalog_path).open("r", encoding="utf-8") as handle:
            self.catalog = json.load(handle)

        self.intent_recognizer = IntentRecognizer(intent_config["intents"])
        self.sentiment_analyzer = SentimentAnalyzer()
        self.order_service = order_service
        self.session_service = session_service
        self.category_aliases = {
            "fashion items": "fashion",
            "fashion item": "fashion",
            "fashions": "fashion",
            "accessories items": "accessories",
            "accessory items": "accessories",
            "electronic items": "electronics",
            "electronics items": "electronics",
            "grocery items": "groceries",
            "book items": "books",
        }

    def process_message(self, message: str, session_id: str | None) -> dict:
        session_id, session = self.session_service.get_or_create(session_id)
        normalized_message = message.strip().lower()
        if normalized_message in {"place this order", "confirm order", "confirm", "select this"}:
            response_text, quick_replies, follow_up_updates = self._confirm_selected_item(session)
            if follow_up_updates:
                session = self.session_service.update(session_id, follow_up_updates)
            return {
                "session_id": session_id,
                "intent": "place_order",
                "confidence": 1.0,
                "sentiment": session["sentiment"],
                "context": session,
                "response": response_text,
                "quick_replies": quick_replies,
            }
        if normalized_message in {"back", "go back", "previous", "back button"}:
            response_text, quick_replies, follow_up_updates = self._handle_back_navigation(session)
            if follow_up_updates:
                session = self.session_service.update(session_id, follow_up_updates)
            return {
                "session_id": session_id,
                "intent": "place_order",
                "confidence": 1.0,
                "sentiment": session["sentiment"],
                "context": session,
                "response": response_text,
                "quick_replies": quick_replies,
            }

        entities = extract_entities(message)
        sentiment = self.sentiment_analyzer.classify(message)

        negative_count = session["negative_count"] + (1 if sentiment == "negative" else 0)
        if sentiment != "negative":
            negative_count = 0

        detected_intent, confidence = self.intent_recognizer.detect_intent(message)
        if confidence < 0.35:
            detected_intent = "fallback"
        detected_intent, confidence = self._resolve_contextual_intent(
            detected_intent=detected_intent,
            confidence=confidence,
            session=session,
            entities=entities,
        )

        updates = {
            "sentiment": sentiment,
            "negative_count": negative_count,
            "previous_intent": detected_intent,
        }
        if entities.get("user_name"):
            updates["user_name"] = entities["user_name"]
        if entities.get("order_id"):
            updates["order_id"] = entities["order_id"]
        if entities.get("product_name"):
            updates["product_name"] = self._normalize_product_name(entities["product_name"])
        if entities.get("brand"):
            updates["selected_brand"] = entities["brand"]

        session = self.session_service.update(session_id, updates)

        response_text, quick_replies, follow_up_updates = self._build_response(
            intent=detected_intent,
            session=session,
            entities=entities,
        )
        if follow_up_updates:
            session = self.session_service.update(session_id, follow_up_updates)

        if session["negative_count"] >= 2:
            response_text += " I can connect you with a human agent at +1-800-123-4567 or support@shopai.com."

        LOGGER.info(
            "session=%s intent=%s confidence=%.2f sentiment=%s",
            session_id,
            detected_intent,
            confidence,
            sentiment,
        )

        return {
            "session_id": session_id,
            "intent": detected_intent,
            "confidence": round(confidence, 2),
            "sentiment": sentiment,
            "context": session,
            "response": response_text,
            "quick_replies": quick_replies,
        }

    def _resolve_contextual_intent(
        self,
        detected_intent: str,
        confidence: float,
        session: dict,
        entities: dict,
    ) -> tuple[str, float]:
        has_order_id = bool(entities.get("order_id"))
        previous_intent = session.get("previous_intent")

        if has_order_id and detected_intent == "fallback":
            if previous_intent in {"track_order", "cancel_order"}:
                return previous_intent, max(confidence, 0.82)
            return "track_order", max(confidence, 0.75)

        if entities.get("user_name") and detected_intent == "fallback":
            return "greeting", max(confidence, 0.8)

        if detected_intent == "fallback":
            if session.get("selected_category") or entities.get("brand") or entities.get("product_name"):
                return "place_order", max(confidence, 0.7)

        return detected_intent, confidence

    def _build_response(self, intent: str, session: dict, entities: dict) -> tuple[str, list[str], dict]:
        user_prefix = f"{session['user_name']}, " if session.get("user_name") else ""

        if intent == "greeting":
            if entities.get("user_name") and not any(
                keyword in (entities.get("product_name") or "").lower()
                for keyword in ["fashion", "electronics", "accessories"]
            ):
                return (
                    f"Nice to meet you, {session['user_name']}! How can I help you today? I can track orders, cancel orders, place orders, or answer questions about returns, shipping, and payments.",
                    ["Track order", "Place order", "Returns policy"],
                    {},
                )
            if session.get("user_name"):
                return (
                    f"Hello {session['user_name']}! Welcome to ShopAI. I can help you track, cancel, or place orders, and answer questions about returns, shipping, payments, pricing, and products.",
                    ["Track order", "Place order", "Returns policy"],
                    {},
                )
            return (
                "Hello! Welcome to ShopAI. I can help you track, cancel, or place orders, and answer questions about returns, shipping, payments, pricing, and products. What is your name?",
                ["Track order", "Place order", "Returns policy"],
                {},
            )

        if intent == "track_order":
            order_id = entities.get("order_id") or session.get("order_id")
            if not order_id:
                return "Please share your order ID so I can track it.", ["Track order", "Cancel order"], {}
            order = self.order_service.track_order(order_id)
            if order:
                return (
                    f"{user_prefix}order {order_id} for {order['product_name']} is currently {order['status']}.",
                    ["Cancel order", "Returns policy", "Shipping info"],
                    {},
                )
            return f"I couldn't find order {order_id}. Please double-check the ID.", ["Track order", "Contact support"], {}

        if intent == "cancel_order":
            order_id = entities.get("order_id") or session.get("order_id")
            if not order_id:
                return "Please provide the order ID you want to cancel.", ["Track order", "Contact support"], {}
            result = self.order_service.cancel_order(order_id)
            return result["message"], ["Track order", "Contact support"], {}

        if intent == "place_order":
            product_name = entities.get("product_name") or session.get("product_name")
            if not product_name:
                return (
                    "Tell me what you want to order. You can name a product or a category like fashion, accessories, electronics, groceries, books, or home decor.",
                    self._with_back([
                        "Buy fashion items",
                        "Buy accessories",
                        "Buy electronics",
                        "Buy groceries",
                        "Buy books",
                    ], session),
                    {},
                )
            normalized_product = self._normalize_product_name(product_name).strip().lower()
            if normalized_product in self.catalog:
                sub_items = self.catalog[normalized_product]
                pretty_category = normalized_product.title()
                if isinstance(sub_items, dict):
                    sub_item_list = ", ".join(item.title() for item in sub_items.keys())
                    return (
                        f"{user_prefix}{pretty_category} includes {sub_item_list}. Tell me which one you want to order.",
                        self._with_back([f"Buy {item.title()}" for item in list(sub_items.keys())[:5]], session),
                        {
                            "selected_category": normalized_product,
                            "selected_subcategory": None,
                            "selected_brand": None,
                            "selected_item": None,
                            "product_name": normalized_product,
                        },
                    )
                sub_item_list = ", ".join(sub_items)
                return (
                    f"{user_prefix}{pretty_category} includes {sub_item_list}. Tell me which one you want to order.",
                    self._with_back([f"Buy {item}" for item in sub_items[:5]], session),
                    {
                        "selected_category": normalized_product,
                        "selected_subcategory": None,
                        "selected_brand": None,
                        "selected_item": None,
                        "product_name": normalized_product,
                    },
                )
            category = session.get("selected_category")
            if category and category in self.catalog and isinstance(self.catalog[category], dict):
                subcatalog = self.catalog[category]
                if normalized_product in subcatalog:
                    brand_or_items = subcatalog[normalized_product]
                    updates = {
                        "selected_subcategory": normalized_product,
                        "product_name": normalized_product,
                    }
                    if isinstance(brand_or_items, dict):
                        return (
                            f"{user_prefix}{normalized_product.title()} is available from {', '.join(brand_or_items.keys())}. Which brand do you want?",
                            self._with_back([f"Buy {brand}" for brand in list(brand_or_items.keys())[:5]], session),
                            {
                                "selected_subcategory": normalized_product,
                                "product_name": normalized_product,
                                "selected_item": None,
                            },
                        )
                    if category == "electronics" and normalized_product == "phones":
                        return (
                            f"{user_prefix}Phones are available from {', '.join(brand_or_items.keys())}. Which brand do you want?",
                            self._with_back([f"Buy {brand}" for brand in list(brand_or_items.keys())[:5]], session),
                            {
                                "selected_subcategory": normalized_product,
                                "product_name": normalized_product,
                            },
                        )
                        return (
                            f"{user_prefix}{normalized_product.title()} options include {', '.join(brand_or_items)}. Tell me which one you want to order.",
                            self._with_back([f"Buy {item}" for item in brand_or_items[:5]], session),
                            {
                                "selected_subcategory": normalized_product,
                                "product_name": normalized_product,
                                "selected_item": None,
                            },
                        )

            selected_category = session.get("selected_category")
            selected_subcategory = session.get("selected_subcategory")
            selected_brand = entities.get("brand") or session.get("selected_brand")
            if selected_category == "electronics" and selected_subcategory == "phones":
                phone_catalog = self.catalog["electronics"]["phones"]
                if selected_brand and selected_brand in phone_catalog and normalized_product == selected_brand.lower():
                    model_prices = phone_catalog[selected_brand]
                    return (
                        f"{user_prefix}{selected_brand} phone models include {', '.join(f'{model} (${price})' for model, price in model_prices.items())}. Which model do you want?",
                        self._with_back([f"Buy {model}" for model in list(model_prices.keys())[:5]], session),
                        {
                            "selected_brand": selected_brand,
                            "product_name": selected_brand,
                            "selected_item": None,
                        },
                    )
                matched_model, matched_price = self._find_phone_model(product_name, selected_brand)
                if matched_model:
                    return (
                        f"{user_prefix}You selected {matched_model} for ${matched_price}. Click 'Place this order' to confirm.",
                        ["Place this order", "Back"],
                        {
                            "selected_item": matched_model,
                            "product_name": matched_model,
                        },
                    )

            matched_leaf_item = self._find_leaf_item(selected_category, selected_subcategory, product_name)
            if matched_leaf_item:
                return (
                    f"{user_prefix}You selected {matched_leaf_item}. Click 'Place this order' to confirm.",
                    ["Place this order", "Back"],
                    {
                        "selected_item": matched_leaf_item,
                        "product_name": matched_leaf_item,
                    },
                )

            order = self.order_service.create_order(product_name)
            return (
                f"{user_prefix}your order for {order['product_name']} has been placed. "
                f"Order ID: {order['order_id']}. Status: {order['status']}. Price: ${order['price']}.",
                ["Track order", "Shipping info", "Returns policy"],
                {
                    "selected_category": None,
                    "selected_subcategory": None,
                    "selected_brand": None,
                    "selected_item": None,
                    "product_name": order["product_name"],
                },
            )

        if intent == "contact_support":
            return (
                "You can reach customer support at +1-800-123-4567 or support@shopai.com.",
                ["Call support", "Email support"],
                {},
            )

        if intent == "product_info":
            product_name = entities.get("product_name")
            if product_name:
                return (
                    f"{user_prefix}{product_name.title()} is available with Prime-style delivery, secure checkout, and easy returns.",
                    ["Pricing", "Place order"],
                    {},
                )

        if intent in self.responses:
            payload = self.responses[intent]
            return f"{user_prefix}{payload['text']}".strip(), payload["quick_replies"], {}

        payload = self.responses["fallback"]
        return payload["text"], payload["quick_replies"], {}

    def _with_back(self, items: list[str], session: dict) -> list[str]:
        quick_replies = list(items)
        if session.get("selected_category") or session.get("selected_subcategory") or session.get("selected_brand"):
            quick_replies.append("Back")
        return quick_replies

    def _handle_back_navigation(self, session: dict) -> tuple[str, list[str], dict]:
        category = session.get("selected_category")
        subcategory = session.get("selected_subcategory")
        brand = session.get("selected_brand")

        if brand and category == "electronics" and subcategory == "phones":
            phone_brands = list(self.catalog["electronics"]["phones"].keys())
            return (
                f"Phones are available from {', '.join(phone_brands)}. Which brand do you want?",
                [f"Buy {item}" for item in phone_brands[:5]] + ["Back"],
                {"selected_brand": None, "selected_item": None, "product_name": "phones"},
            )

        if subcategory and category in self.catalog and isinstance(self.catalog[category], dict):
            options = self.catalog[category]
            option_labels = list(options.keys())
            return (
                f"{category.title()} includes {', '.join(item.title() for item in option_labels)}. Tell me which one you want to order.",
                [f"Buy {item.title()}" for item in option_labels[:5]] + ["Back"],
                {"selected_subcategory": None, "selected_brand": None, "selected_item": None, "product_name": category},
            )

        if category and category in self.catalog:
            options = self.catalog[category]
            return (
                "Tell me what you want to order. You can name a product or a category like fashion, accessories, electronics, groceries, books, or home decor.",
                [
                    "Buy fashion items",
                    "Buy accessories",
                    "Buy electronics",
                    "Buy groceries",
                    "Buy books",
                ],
                {"selected_category": None, "selected_subcategory": None, "selected_brand": None, "selected_item": None, "product_name": None},
            )

        return (
            "Tell me what you want to order. You can name a product or a category like fashion, accessories, electronics, groceries, books, or home decor.",
            [
                "Buy fashion items",
                "Buy accessories",
                "Buy electronics",
                "Buy groceries",
                "Buy books",
            ],
            {"selected_category": None, "selected_subcategory": None, "selected_brand": None, "selected_item": None, "product_name": None},
        )

    def _find_phone_model(self, product_name: str, selected_brand: str | None) -> tuple[str | None, float | None]:
        phone_catalog = self.catalog["electronics"]["phones"]
        normalized_name = product_name.strip().lower()

        brands_to_search = [selected_brand] if selected_brand else list(phone_catalog.keys())
        for brand in brands_to_search:
            if brand not in phone_catalog:
                continue
            for model, price in phone_catalog[brand].items():
                if model.lower() == normalized_name:
                    return model, price
        return None, None

    def _normalize_product_name(self, product_name: str) -> str:
        normalized = product_name.strip().lower()
        return self.category_aliases.get(normalized, normalized)

    def _find_leaf_item(self, category: str | None, subcategory: str | None, product_name: str) -> str | None:
        if not category or not subcategory:
            return None
        if category not in self.catalog or not isinstance(self.catalog[category], dict):
            return None
        subcatalog = self.catalog[category]
        if subcategory not in subcatalog or not isinstance(subcatalog[subcategory], list):
            return None

        normalized_name = self._normalize_product_name(product_name)
        for item in subcatalog[subcategory]:
            if item.lower() == normalized_name:
                return item
        return None

    def _confirm_selected_item(self, session: dict) -> tuple[str, list[str], dict]:
        selected_item = session.get("selected_item")
        if not selected_item:
            return (
                "Please choose an item first, then I can place the order for you.",
                self._with_back(["Buy fashion items", "Buy electronics", "Buy accessories"], session),
                {},
            )

        matched_model, matched_price = self._find_phone_model(selected_item, session.get("selected_brand"))
        order = self.order_service.create_order(matched_model or selected_item, matched_price)
        return (
            f"Your order for {order['product_name']} has been placed. Order ID: {order['order_id']}. Status: {order['status']}. Price: ${order['price']}.",
            ["Track order", "Shipping info", "Returns policy"],
            {
                "selected_category": None,
                "selected_subcategory": None,
                "selected_brand": None,
                "selected_item": None,
                "product_name": order["product_name"],
            },
        )
