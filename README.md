# 🤖 Phani AI - Intelligent Real-time Assistant

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.60.0-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/Gemini_API-2.5-4285F4.svg)](https://deepmind.google/technologies/gemini/)

An intelligent conversational AI assistant built with **Python**, **Streamlit**, **TF-IDF Intent Classification**, **Rule-based NER**, and **Google Gemini AI (`google-genai`)** integration.

---

### ✨ Key Features
- 🧠 **Google Gemini Neural Engine**: Real-time LLM responses (`gemini-2.5-flash`).
- 🎯 **High Confidence Classifier**: TF-IDF & Cosine Similarity vectorizer (88%–98% confidence).
- 🏷️ **Entity Extractor (NER)**: Extracts Order IDs, Emails, Dates, and Amounts.
- ⚡ **Live Inspector HUD**: Sidebar tracking intent, confidence, entities, and latency.
- 🎭 **3 Personas**: Customer Support, Virtual Assistant, and FAQ Automation.

---

### 🚀 Quick Start
```bash
# 1. Install dependencies
python3 -m pip install -r requirements.txt

# 2. Run Phani AI
python3 -m streamlit run streamlit_app.py
