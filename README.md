# AI Customer Service Chatbot

Production-ready Flask chatbot for an Amazon-like e-commerce platform. The app supports order tracking, cancellation, order placement, FAQ handling, support escalation, context-aware conversations, and a responsive chat UI.

## Folder Structure

```text
ecommerce-ai-chatbot/
├── app/
│   ├── __init__.py
│   └── routes.py
├── data/
│   ├── catalog.json
│   ├── intents.json
│   ├── orders.json
│   └── responses.json
├── nlp/
│   ├── __init__.py
│   ├── entity_extractor.py
│   ├── intent_recognizer.py
│   └── sentiment.py
├── services/
│   ├── __init__.py
│   ├── chat_service.py
│   ├── order_service.py
│   └── session_service.py
├── static/
│   ├── app.js
│   └── styles.css
├── templates/
│   └── index.html
├── requirements.txt
└── run.py
```

## Features

- Regex-based intent recognition with confidence scoring
- Context-aware sessions with session IDs, user name, order ID, previous intent, and sentiment
- TextBlob sentiment analysis with repeated negative sentiment escalation
- JSON-backed order store and chatbot response catalog
- Category catalog with sub-item suggestions for order placement
- REST API endpoints for chat and order workflows
- Responsive WhatsApp-style chat frontend with quick replies and typing indicator

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python run.py
   ```

4. Open `http://127.0.0.1:5000`.

## API Endpoints

- `POST /chat`
- `POST /order/track`
- `POST /order/cancel`
- `POST /order/create`

## Sample Requests

```bash
curl -X POST http://127.0.0.1:5000/chat -H "Content-Type: application/json" -d "{\"message\": \"Track order ORD102938\"}"
curl -X POST http://127.0.0.1:5000/order/create -H "Content-Type: application/json" -d "{\"product_name\": \"Bluetooth Speaker\"}"
```

## Notes

- Orders are persisted in `data/orders.json`.
- For real production use, replace the JSON data layer with a database and move the secret key into environment variables.
- This project includes placeholders that can be extended with real e-commerce APIs or a lightweight ML classifier.
