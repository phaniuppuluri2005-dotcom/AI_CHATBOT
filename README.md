# 🤖 Phani AI - Intelligent AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.60.0-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Google_Gemini_API-2.5-4285F4.svg)](https://ai.google.dev/)

**Phani AI** is a general-purpose AI assistant built with **Python, Streamlit, and Google Gemini AI**. It understands natural-language queries and dynamically provides answers, explanations, coding assistance, data-analysis support, and access to specialized live services.

The goal is simple:

> **Ask Phani AI anything.**

---

## ✨ Key Features

* 🧠 **AI-Powered Responses** — Uses Google Gemini for natural-language understanding and intelligent responses.
* 💬 **General-Purpose Assistant** — Ask questions about programming, DSA, Data Science, science, mathematics, engineering, education, career, research, and other topics.
* 🔄 **Context-Aware Conversations** — Understands follow-up questions using previous conversation context.
* 🎯 **Adaptive Responses** — Adjusts explanations based on instructions such as `briefly`, `in detail`, `simply`, `with example`, and `step by step`.
* 🐍 **Programming Assistance** — Supports Python, Java, SQL, HTML, CSS, JavaScript, and other programming-related questions.
* 🧩 **DSA Assistance** — Explains algorithms, data structures, coding problems, and problem-solving approaches.
* 📊 **Data Analysis** — Supports CSV/Excel analysis using Python, Pandas, and NumPy.
* 🎬 **Movie Information** — Retrieves verified movie information from external movie services.
* 📍 **Location & Maps** — Provides location information and Google Maps links.
* 💱 **Currency Conversion** — Supports currency conversion using live exchange-rate services.
* 🌦️ **Live Services** — Supports services such as weather, cricket scores, cryptocurrency prices, and other current information when requested.
* 🔐 **Authentication & Data Storage** — Supports user authentication and persistent conversation storage.

---

## 🧠 Intelligent Query Processing

Phani AI does not require users to select a topic before asking a question.

Instead, queries are processed dynamically:

```text
User Query
    ↓
Query Preprocessing
    ↓
Typo Normalization
    ↓
Intent & Topic Detection
    ↓
Service Routing
    ↓
AI / Specialized Service
    ↓
Response Validation
    ↓
Final Response
```

For example:

```text
"What is Python?"
        ↓
General AI

"Explain Python lists briefly"
        ↓
General AI + concise response

"Current Bitcoin price"
        ↓
Live Cryptocurrency Service

"What is the weather in Hyderabad?"
        ↓
Weather Service

"Tell me about Inception"
        ↓
Movie Service
```

---

## 💡 Example Queries

### General Questions

```text
What is machine learning?
Explain photosynthesis.
Tell me about economics.
What is blockchain?
```

### Programming & DSA

```text
Explain stacks simply.
Solve Two Sum in Python.
What is sliding window?
Fix this SQL query.
Explain linked lists with an example.
```

### Data Analytics

```text
What is Power BI?
Explain DAX.
What is the difference between Tableau and Power BI?
Analyze this CSV file.
```

### Learning

```text
Teach me Python step by step.
Give me 20 SQL interview questions.
Create a 30-day DSA study plan.
Explain recursion for a beginner.
```

### Current Information

```text
What is the current Bitcoin price?
What is the weather in Hyderabad?
What is the current cricket score?
Convert 100 USD to INR.
```

### Movies

```text
Tell me about Inception.
Tell me about They Call Him OG.
Who directed Avatar?
```

### Locations

```text
Where is Charminar?
Show me the Taj Mahal on Google Maps.
Give me directions from Hyderabad to Vijayawada.
```

---

## 🛠️ Technology Stack

### Backend & Application

* Python
* Streamlit

### AI

* Google Gemini API
* `google-genai`
* Natural Language Processing
* Intent Detection
* Query Routing

### Data Analysis

* Pandas
* NumPy

### Database

* SQLite for development
* PostgreSQL for production

### Version Control

* Git
* GitHub

### External Services

* Weather API
* Movie information API
* Maps
* Currency exchange API
* Cryptocurrency API
* Cricket/live-data services

---

## 📁 Project Structure

```text
AI_CHATBOT/
│
├── app.py
├── aichatapp.py
├── nlp_engine.py
│
├── auth/
│   └── ...
│
├── components/
│   └── ...
│
├── config/
│   └── ...
│
├── database/
│   └── ...
│
├── services/
│   └── ...
│
├── tests/
│   └── ...
│
├── utils/
│   └── ...
│
├── .streamlit/
│   └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/phaniuppuluri2005-dotcom/AI_CHATBOT.git
cd AI_CHATBOT
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Configure API keys

Create a `.env` file using `.env.example`:

```env
GEMINI_API_KEY=your_api_key
```

Add any other required service API keys according to the project configuration.

**Do not commit `.env` or private API keys to GitHub.**

### 4. Run Phani AI

```bash
python3 -m streamlit run app.py
```

---

## 🔐 Security

Phani AI follows basic security practices including:

* User authentication
* User-specific conversation access
* Environment-based API keys
* Input validation
* API timeout and error handling
* Database access control
* Protection of sensitive credentials

---

## 🧪 Testing

Run the available tests with:

```bash
python run_tests.py
```

---

## 🎯 Project Objective

The objective of Phani AI is to develop a **general-purpose intelligent assistant** that can understand natural-language requests and dynamically determine the appropriate way to respond.

Instead of relying on fixed topic menus, users can interact with Phani AI naturally and ask questions across different domains.

The project focuses on:

* AI-powered conversations
* Natural-language understanding
* Context-aware responses
* Intelligent service routing
* Programming assistance
* DSA learning
* Data analysis
* Educational support
* Real-time information services
* External API integration

---

## 🔮 Future Improvements

* Improved conversational memory
* More live-data integrations
* Advanced data-analysis capabilities
* Improved response personalization
* Better authentication and authorization
* PostgreSQL production architecture
* Background task processing
* Performance optimization
* Automated testing and CI/CD
* Scalable deployment architecture

---

## 👨‍💻 Developer

**PHANINDRA**

B.Tech - Data Science
India

---

## 📄 License

This project is currently intended for educational, development, and portfolio purposes.
