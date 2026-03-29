# AI-E-Commerce-Customer-Service-Chatbot
Flask-based AI customer service chatbot for e-commerce platforms with order tracking, cancellations, order placement, FAQs, sentiment detection, context-aware replies, and a custom chat UI.

An intelligent, full-stack customer service chatbot designed for an Amazon-like e-commerce platform. Built using Flask, Python, HTML, CSS, and JavaScript, this project simulates a real-world virtual shopping assistant that enhances user experience through interactive and context-aware conversations.

The chatbot is capable of handling key customer support operations such as order tracking, order cancellation, placing new orders, answering FAQs, and providing support contact details. It goes beyond a basic rule-based bot by incorporating intent recognition, entity extraction (like order IDs and user names), and sentiment analysis using TextBlob to deliver more personalized and relevant responses.

A standout feature of this project is its guided shopping experience. Users can seamlessly navigate through product categories such as electronics and fashion, explore subcategories, choose brands, and finalize their selections through a structured conversational flow. The chatbot maintains session context, allowing it to remember user inputs and provide a more natural and continuous interaction.

The backend follows a modular Flask architecture with clearly separated layers for routing, business logic, NLP processing, and data management. On the frontend, a modern chat interface is implemented with features like a floating chatbot launcher, quick reply options, typing indicators, timestamps, and custom branding for an engaging user experience.

Data is managed using JSON files, making the application lightweight, easy to understand, and simple to extend or customize.

This project effectively demonstrates full-stack development, applied natural language processing, conversational UI design, and automation of e-commerce workflows, making it a strong addition to any developer portfolio or GitHub showcase.

Technologies Used

This project integrates backend development, frontend design, and lightweight NLP techniques to create a complete conversational support system.

Backend
Python for core application logic
Flask for building RESTful APIs and managing routes
Frontend
HTML5 for structure
CSS3 for styling, branding, animations, and responsive chat UI
Vanilla JavaScript for dynamic interactions, API communication, and chat handling
NLP & Chat Intelligence
Regular Expressions (Regex) for intent detection and entity extraction
TextBlob for sentiment analysis
Context-aware session handling for maintaining conversation flow and personalization
Data Storage
JSON files for:
chatbot intents
response templates
product catalog
sample order data
UI/UX Features
Floating chatbot launcher with custom branding
Guided multi-step product selection flow
Category and subcategory navigation
Back navigation for better usability
Order confirmation step before final placement
