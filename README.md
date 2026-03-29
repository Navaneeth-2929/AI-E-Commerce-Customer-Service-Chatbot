<<<<<<< HEAD
# AI E-Commerce Customer Service Chatbot

An AI-powered customer service chatbot for an Amazon-like e-commerce platform, built with Flask, Python, HTML, CSS, and JavaScript.

The chatbot helps users:
- track orders
- cancel orders
- place new orders
- browse categories and sub-categories
- get support contact details
- ask FAQ-style questions about returns, shipping, payments, pricing, and product information

It also includes:
- regex-based intent recognition
- entity extraction
- TextBlob-based sentiment analysis
- session-aware conversation context
- quick replies and guided order flow
- floating chatbot launcher UI

## Project Overview

This project simulates a production-style customer support assistant for an e-commerce application. It combines a modular Flask backend with a conversational frontend and a lightweight NLP layer.

Instead of using a large external AI API, the chatbot uses:
- regex-based intent matching for speed and simplicity
- JSON files for lightweight storage
- TextBlob for sentiment detection
- in-memory session tracking for personalization and conversational continuity

The result is a practical full-stack chatbot project that is easy to run locally, easy to understand, and easy to extend.

## Key Features

### Customer Support Features
- Greeting and farewell handling
- User name capture and personalized responses
- Order tracking by order ID
- Order cancellation with validation
- New order creation
- FAQ support for returns, shipping, payments, pricing, and product information
- Human support escalation on repeated negative sentiment

### Conversational Features
- Session ID-based context handling
- Previous intent tracking
- Order ID memory
- Product and category memory
- Brand/model guided conversation for phone orders
- Back navigation within guided catalog flows
- Confirmation step before placing final selected orders

### Frontend Features
- Floating chatbot launcher with custom logo
- Open/close chatbot panel
- Chat-style messaging interface
- Quick reply buttons
- Typing indicator
- Message timestamps
- Sentiment indicator
- Custom background image support
- Hover effects and glow for chatbot launcher

## Technologies Used

### Backend
- Python 3
- Flask 3.1.0

### NLP / AI Logic
- Regex for intent detection
- Regex for entity extraction
- TextBlob 0.19.0 for sentiment analysis

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

### Data Layer
- JSON files for intents, responses, orders, and catalog data

### Development Style
- Modular Flask structure
- Service-based backend organization
- Separate NLP layer
- Separate templates and static assets

## Project Structure

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
│   ├── background image.png
│   ├── chatbot background.png
│   ├── chatbot logo.png
│   └── styles.css
├── templates/
│   └── index.html
├── requirements.txt
├── README.md
└── run.py
```

## How the Project Works

### 1. Chat Flow
The frontend sends a user message to the backend using the `/chat` endpoint.

The backend then:
1. reads the session
2. extracts entities such as name, order ID, product, brand, or category
3. detects sentiment
4. predicts the intent using regex patterns
5. builds a contextual response
6. returns the response and suggested quick replies

### 2. Order Flow
The order flow supports both direct ordering and guided ordering.

Examples:
- `Track order ORD102938`
- `Cancel order ORD564738`
- `Buy electronics`
- `Buy phones`
- `Buy Apple`
- `Buy iPhone 15`
- `Place this order`

### 3. Session Context
Each conversation stores:
- `user_name`
- `order_id`
- `product_name`
- `selected_category`
- `selected_subcategory`
- `selected_brand`
- `selected_item`
- `previous_intent`
- `sentiment`
- `negative_count`

This makes responses more personalized and allows the chatbot to continue guided flows.

## Intent Categories

The chatbot currently supports these intent categories:
- greeting
- goodbye
- track_order
- cancel_order
- place_order
- returns
- shipping
- payments
- pricing
- product_info
- contact_support
- fallback

## Entity Extraction

The chatbot extracts:
- Order ID
- User name
- Product names
- Categories
- Brands
- Phone models

Example supported user name formats:
- `I am Rahul`
- `I'm Priya`
- `im nava`
- `my self nava`
- `my name is Asha`

## Sentiment Analysis

Sentiment analysis is implemented using TextBlob.

Supported sentiment classes:
- positive
- neutral
- negative

If negative sentiment is detected repeatedly, the chatbot escalates to human support:
- Phone: `+1-800-123-4567`
- Email: `support@shopai.com`

## API Endpoints

### `POST /chat`
Handles chatbot conversation.

Request:

```json
{
  "message": "Track order ORD102938",
  "session_id": "optional-session-id"
}
```

Response:

```json
{
  "session_id": "generated-or-existing-session-id",
  "intent": "track_order",
  "confidence": 0.8,
  "sentiment": "neutral",
  "context": {
    "user_name": "Rahul",
    "order_id": "ORD102938"
  },
  "response": "Rahul, order ORD102938 for Noise Cancelling Headphones is currently shipped.",
  "quick_replies": ["Cancel order", "Returns policy", "Shipping info"]
}
```

### `POST /order/track`
Tracks an order by order ID.

Request:

```json
{
  "order_id": "ORD102938"
}
```

### `POST /order/cancel`
Cancels an order if it is eligible.

Request:

```json
{
  "order_id": "ORD564738"
}
```

### `POST /order/create`
Creates a new order.

Request:

```json
{
  "product_name": "Bluetooth Speaker"
}
```

## Sample Usage

### Greeting and Name
```text
hello
my name is navaneeth
```

### Track Order
```text
track my order
ORD102938
```

### Cancel Order
```text
cancel my order
ORD564738
```

### Guided Electronics Ordering
```text
buy electronics
buy phones
buy apple
buy iphone 15
place this order
```

### Guided Fashion Ordering
```text
buy fashion items
buy t-shirts
buy graphic t-shirts
place this order
```

## Catalog and Data Files

### `data/orders.json`
Stores sample order records with fields:
- `order_id`
- `product_name`
- `status`
- `price`

### `data/intents.json`
Stores regex patterns for supported intents.

### `data/responses.json`
Stores canned text responses and quick reply suggestions.

### `data/catalog.json`
Stores category, sub-category, brand, and model data used by the guided order flow.

## Setup Instructions

### 1. Open the project folder

```bash
cd C:\Users\HP\OneDrive\Documents\Playground\ecommerce-ai-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

For Git Bash:

```bash
source .venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Flask application

```bash
python run.py
```

### 6. Open in browser

```text
http://127.0.0.1:5000
```

## How to Use the UI

1. Open the app in the browser.
2. Click the floating chatbot logo.
3. Start the conversation.
4. Use quick reply buttons for guided ordering.
5. Use the `Back` button to move up one level in guided flows.
6. Use `Place this order` to confirm a final selected item.

## Current Visual Customizations

The project currently supports:
- custom page background image
- custom chatbot launcher logo
- custom chatbot panel background image
- glow and hover animation on launcher

You can replace images in the `static/` folder to re-theme the chatbot.

## Requirements

```text
Flask==3.1.0
textblob==0.19.0
```

## Limitations

- Session data is stored in memory, so restarting the server resets active conversations.
- Orders are stored in JSON instead of a database.
- No authentication or user login is implemented.
- Regex-based intent detection is simple and fast, but not as flexible as a full ML/NLP model.
- The project currently uses static sample datasets for products and orders.

## Possible Improvements

- Add SQLite or PostgreSQL for persistence
- Add user authentication
- Add admin dashboard
- Add real payment and order APIs
- Add product images and richer catalog browsing
- Add ML-based intent classification
- Add multilingual support
- Add automated tests
- Add Docker support
- Deploy to Render, Railway, or AWS

## Why This Project Is Useful

This project is a strong full-stack portfolio project because it demonstrates:
- backend API development with Flask
- modular Python architecture
- frontend chat UI development
- practical NLP logic
- stateful conversation design
- sentiment-aware support behavior
- e-commerce workflow automation

## Authoring Notes

This project is designed to be easy to understand, easy to demo, and easy to extend for internships, academic submissions, personal portfolios, and GitHub showcases.

If you plan to push it to GitHub, this README is already structured to work well as a project landing page.
=======
