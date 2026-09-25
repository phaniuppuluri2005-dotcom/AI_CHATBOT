# PHANI AI — GENERAL-PURPOSE AI PLATFORM

> **Phani AI** is a general-purpose AI platform that combines conversational intelligence, real-time information, multimodal generation, data analysis, and intelligent tool orchestration in a unified experience.

---

## 💡 Universal Topic Explanation System

1. **Zero Hardcoded Topic Fallbacks**: All static fallback responses (`if topic == "Stacks": ...`) have been eliminated. The Google Gemini 2.5 AI model serves as the general-purpose knowledge engine for **virtually any topic** across 50+ domains (Physics, Computer Science, Mathematics, Engineering, Medicine, Economics, Law, History, Philosophy, Literature, Culture, Space, Agriculture, General Knowledge).
2. **Natural-Language Parameter Parser (`services/student_service.py`)**:
   - Parses natural-language inputs like *"Explain quantum computing briefly for a beginner with an example"* into:
     - **Topic:** Quantum Computing
     - **Length:** Brief
     - **Level:** Beginner
     - **Instruction:** Include a real-world example
3. **Free-Form Natural Language UI (`components/student_ui.py`)**:
   - Unconstrained free-form input (`[ Ask about any topic... ]`).
   - Users are never forced into choosing from fixed dropdown categories.
4. **Dynamic Quiz & SQL Practice Generator**:
   - Generates interactive practice quizzes for **any** user-requested topic dynamically using AI reasoning.

---

## 🏏 Live Cricket Data Engine (Critical Live Requirement)

1. **Zero Fabricated Scores**: Queries requesting current cricket scores (`"cricket score"`, `"live cricket score"`, `"India cricket score"`, `"who is winning?"`, `"criket score"`) route directly to live XML data feeds (ESPN Cricinfo Official Live RSS).
2. **Never Uses Gemini Memory for Live Scores**: Gemini's model memory is strictly isolated from live scores to prevent hallucinated or stale score outputs. If the live feed is unavailable, the system explicitly returns:
   `"Live cricket data is currently unavailable. Please try again shortly."`
3. **Strict Match Status Classification**:
   - `🔴 LIVE`: Active overs, wickets, current run rates, active batters.
   - `✅ COMPLETED`: Final result and winner details.
   - `⏰ UPCOMING`: Scheduled match time and teams.
   - `ℹ️ NO MATCH`: Clear notice when no match matches the user's request.
4. **Short-Lived Caching & Timestamps**: Max 60-second TTL cache with `last_updated` timestamps on every card.

---

## 🌟 Key Platform Capabilities

1. **Conversational AI Core**: Multi-turn reasoning powered by Google Gemini 2.5 LLM with context retention and persona modes.
2. **Adaptive Response Length Engine**: Responds according to explicit user style instructions (`brief`, `detailed`, `beginner`, `code_only`, `summary`).
3. **Central AI Orchestrator**: Handles single & multi-intent task pipelines (e.g. *"Explain photosynthesis briefly AND create an image to help me understand it"*).
4. **Data Analysis Engine**: Upload CSV, Excel (`.xlsx`), or JSON datasets for automated statistics, missing value audits, top value counts, and interactive charts (Bar, Line, Scatter, Pie) using Pandas and Streamlit.
5. **Multimodal Vision Studio**: Upload images (PNG, JPG) for Visual Q&A, diagram explanations, OCR text extraction, and error screenshot diagnosis.
6. **Real-Time Information Services**: Live weather forecasts (Open-Meteo), Cricinfo cricket scores, breaking news (Google News RSS), stock ticker prices (Yahoo Finance), crypto market stats (CoinGecko), forex currency conversion (ExchangeRate API), maps geocoding (OpenStreetMap), movies, dictionary, and Wikipedia knowledge lookup.
7. **Multimedia Generation**: Digital Image Studio (Pollinations AI / Imagen) and Asynchronous Video Studio (Phani Motion Studio).
8. **Document / PDF AI**: PDF and DOCX text extraction, structured summarization, resume analysis, and interview question generation.
9. **Authentication & User Data Isolation**: Password hashing (`PBKDF2-HMAC-SHA256`), user sign in/registration, and server-side data isolation ensuring users ONLY see their own history, saved items, images, and files.
10. **Protected Admin System & Benchmark Evaluation**: Restricted Administrator system (`role == 'admin'`) with global analytics and quality control benchmark testing across factual accuracy, intent routing, latency, and failure rates.

---

## 🚀 Quick Start & Local Development

### 1. Installation
```bash
git clone https://github.com/phani/AI_CHATBOT.git
cd AI_CHATBOT
python3 -m pip install -r requirements.txt
```

### 2. Run Application
```bash
streamlit run app.py
```

### 3. Run Automated Test Suite
```bash
python3 run_tests.py
```
