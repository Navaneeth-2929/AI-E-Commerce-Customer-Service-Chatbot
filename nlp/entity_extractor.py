import re


ORDER_ID_PATTERN = re.compile(r"\bORD\d{6}\b", re.IGNORECASE)
NAME_PATTERN = re.compile(
    r"\b(?:i am|i'm|im|my name is|myself|my self|this is|name is)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\b",
    re.IGNORECASE,
)
CATEGORY_PATTERN = re.compile(
    r"\b("
    r"fashion|clothing|men'?s wear|women'?s wear|kids wear|"
    r"accessories|accessories items|bags|watches|jewelry|jewellery|"
    r"electronics|gadgets|mobiles|laptops|appliances|"
    r"groceries|books|home decor|furniture|beauty|toys|sports|"
    r"phones|headphones|smartwatches|tablets|t-shirts|jeans|dresses|sneakers|jackets|"
    r"sunglasses|belts|wallets|rice|cooking oil|coffee|snacks|milk|novels|self-help books|"
    r"comics|academic books|biographies|wall art|lamps|curtains|cushions|rugs|lipstick|"
    r"moisturizer|perfume|face wash|shampoo|action figures|building blocks|dolls|board games|"
    r"puzzles|cricket bat|football|yoga mat|dumbbells|running shoes"
    r")\b",
    re.IGNORECASE,
)
BRAND_PATTERN = re.compile(
    r"\b(apple|samsung|oneplus|google|xiaomi)\b",
    re.IGNORECASE,
)
MODEL_PATTERN = re.compile(
    r"\b("
    r"iphone 15|iphone 15 pro|iphone 14|iphone se|"
    r"galaxy s24|galaxy s24 ultra|galaxy a55|galaxy z flip 6|"
    r"oneplus 12|oneplus 12r|nord ce 4|"
    r"pixel 8|pixel 8 pro|pixel 7a|"
    r"xiaomi 14|redmi note 13 pro|poco x6"
    r")\b",
    re.IGNORECASE,
)
PRODUCT_PATTERN = re.compile(
    r"\b(?:buy|purchase|get|place an order for|place order for)\s+([a-zA-Z0-9][a-zA-Z0-9\s\-]{1,50})",
    re.IGNORECASE,
)


def extract_entities(text: str) -> dict:
    entities = {"order_id": None, "user_name": None, "product_name": None, "brand": None}

    order_match = ORDER_ID_PATTERN.search(text)
    if order_match:
        entities["order_id"] = order_match.group(0).upper()

    name_match = NAME_PATTERN.search(text)
    if name_match:
        entities["user_name"] = name_match.group(1).title()

    brand_match = BRAND_PATTERN.search(text)
    if brand_match:
        entities["brand"] = brand_match.group(1).title()

    model_match = MODEL_PATTERN.search(text)
    if model_match:
        entities["product_name"] = model_match.group(1).title()

    product_match = PRODUCT_PATTERN.search(text)
    if product_match and not entities["product_name"]:
        entities["product_name"] = product_match.group(1).strip(" .,!?")
    elif CATEGORY_PATTERN.search(text) and not entities["product_name"]:
        entities["product_name"] = CATEGORY_PATTERN.search(text).group(1).strip(" .,!?")

    return entities
