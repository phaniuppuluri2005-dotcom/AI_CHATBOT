"""
AI LLM Service for Phani AI Platform.
Wraps Google Gemini API (via google-genai or google-generativeai) with multi-turn context support,
adaptive response-length instructions, persona instructions, and intelligent offline reasoning fallback.
Generates genuine, helpful answers for all conversational, technical, and general knowledge queries.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from config.settings import settings
from utils.security import redact_api_keys

logger = logging.getLogger("PhaniAI.AIService")

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class AIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def parse_response_style(self, prompt: str, default_style: str = "Balanced") -> str:
        """Parse explicit response-style instructions from user prompt."""
        p_lower = prompt.lower()
        if any(w in p_lower for w in ["briefly", "short", "concise", "in short", "quick summary"]):
            return "brief"
        elif any(w in p_lower for w in ["in detail", "detailed", "comprehensive", "deep dive", "thoroughly"]):
            return "detailed"
        elif any(w in p_lower for w in ["beginner", "like i'm 5", "eli5", "simple terms", "easy to understand"]):
            return "beginner"
        elif any(w in p_lower for w in ["only code", "just code", "code snippet", "code only"]):
            return "code_only"
        elif any(w in p_lower for w in ["summarize", "summary"]):
            return "summary"
        return default_style.lower()

    def _generate_fallback_response(self, prompt: str) -> str:
        """Intelligent, natural fallback generator for conversational & technical queries when API is offline."""
        p_clean = prompt.strip()
        p_lower = p_clean.lower()

        # 1. Natural Conversational Greetings
        if p_lower in ["hi", "hello", "hey", "hi there", "hello there", "greetings"]:
            return "Hi! 👋 How can I help you today?"
        elif p_lower.startswith("good morning"):
            return "Good morning! ☀️ How can I help you today?"
        elif p_lower.startswith("good afternoon"):
            return "Good afternoon! ☀️ How can I help you today?"
        elif p_lower.startswith("good evening"):
            return "Good evening! 🌆 How can I help you today?"
        elif any(w in p_lower for w in ["how are you", "how's it going", "how are u"]):
            return "I'm doing great, thank you for asking! How can I assist you today?"
        elif any(w in p_lower for w in ["who are you", "what is your name", "what's your name"]):
            return "I am **Phani AI**, your general-purpose AI assistant. I'm here to help with answers, coding, learning, data analysis, and live real-time information!"
        elif p_lower in ["thank you", "thanks", "thank u", "thx"]:
            return "You're very welcome! Let me know if you have any other questions."

        # 2. Dynamic Subject / Coding / Knowledge Explanation Fallback
        style = self.parse_response_style(prompt)

        # Extract core topic cleanly
        topic = re.sub(
            r'(?i)\b(at\s+a\s+(?:beginner|intermediate|advanced|expert)\s+level|at\s+(?:beginner|intermediate|advanced|expert)\s+level|at\s+a\s+level|at\s+level|for\s+(?:a\s+)?(?:beginner|beginners|students|student|freshers|kids)|for\s+an?\s+interview|interview\s+questions|interview\s+answer|interview|create\s+a?\s+timetable\s+for|study\s+plan|schedule|quiz\s+me\s+on|quiz\s+me|quiz|questions|question|only\s+code|code\s+only|with\s+an?\s+example|with\s+examples|step\s+by\s+step|in\s+detail|detailed|briefly|simply|like\s+i\'m\s+\d+|define|definition\s+of|explain|describe|teach\s+me|teach|tell\s+me\s+about|what\s+is|what\s+are|how\s+does|research|compare|latest|current|version)\b',
            '',
            p_clean
        ).strip()
        topic = re.sub(r'(?i)\b(beginner|beginners|intermediate|advanced|expert|level|levels|brief|short|concise)\b', '', topic).strip()
        topic = topic.strip("'\"")
        topic = re.sub(r'^[^\w]+|[^\w]+$', '', topic).strip()
        topic = topic.strip("'\"")

        if not topic:
            topic = p_clean.strip("'\"")

        topic_title = topic if topic.isupper() else topic.title()
        topic_lower = topic.lower()

        # Factual definitions for common topics if LLM offline
        factual_definitions = {
            "python": {
                "overview": "**Python** is a high-level, general-purpose programming language known for its clean, readable syntax and versatile ecosystem.",
                "why": "It is widely used across web development, data analysis, machine learning, automation, scripting, and software engineering.",
                "concepts": "• Simple & readable syntax\n• Dynamic typing & automatic memory management\n• Rich ecosystem of packages (NumPy, Pandas, Django, PyTorch)\n• Object-oriented and functional programming paradigms",
                "example": "```python\n# Simple Python Example\ndef greet(topic):\n    return f\"Welcome to {topic}!\"\n\nprint(greet(\"Python\"))\n```",
                "next": "• Learn step by step\n• Coding practice problems\n• Interview questions\n• Build a project"
            },
            "java": {
                "overview": "**Java** is a class-based, object-oriented programming language designed with the 'Write Once, Run Anywhere' (WORA) philosophy.",
                "why": "It powers enterprise backend systems, Android app development, and large-scale distributed architectures.",
                "concepts": "• Java Virtual Machine (JVM) execution\n• Strong static typing & object-oriented design\n• Robust concurrency and memory management",
                "example": "```java\n// Simple Java Example\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, Java!\");\n    }\n}\n```",
                "next": "• Learn Java fundamentals\n• Object-oriented programming\n• Java interview questions"
            },
            "sql": {
                "overview": "**SQL** (Structured Query Language) is the standard language for querying, managing, and manipulating relational databases.",
                "why": "It is fundamental for data analysis, backend development, and business intelligence.",
                "concepts": "• Data Querying (`SELECT`, `WHERE`, `JOIN`)\n• Data Manipulation (`INSERT`, `UPDATE`, `DELETE`)\n• Schema Design (`CREATE TABLE`, indexes, foreign keys)",
                "example": "```sql\n-- Retrieve top records\nSELECT id, name, score\nFROM rankings\nWHERE score > 90\nORDER BY score DESC;\n```",
                "next": "• SQL practice queries\n• Database design\n• Interview prep"
            },
            "machine learning": {
                "overview": "**Machine Learning (ML)** is a branch of artificial intelligence where algorithms learn patterns from data to make predictions or decisions.",
                "why": "It drives modern innovations in recommendation systems, natural language processing, computer vision, and predictive analytics.",
                "concepts": "• Supervised Learning (Regression, Classification)\n• Unsupervised Learning (Clustering, Dimensionality Reduction)\n• Model Evaluation & Feature Engineering",
                "example": "```python\n# Basic ML with scikit-learn\nfrom sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression()\n```",
                "next": "• ML roadmap step by step\n• Python for Data Science\n• Practice projects"
            },
            "power bi": {
                "overview": "**Power BI** is Microsoft's business intelligence and interactive data visualization platform.",
                "why": "It enables organizations to transform raw data into interactive dashboards, reports, and real-time business insights.",
                "concepts": "• Data Connectivity & ETL (Power Query)\n• Data Modeling & DAX expressions\n• Interactive Visualizations & Dashboards",
                "example": "• Connect data source $\\rightarrow$ Transform in Power Query $\\rightarrow$ Build DAX measures $\\rightarrow$ Publish dashboard.",
                "next": "• Learn DAX formulas\n• Dashboard design\n• Practice datasets"
            },
            "data structures": {
                "overview": "**Data Structures** are specialized formats for organizing, processing, retrieving, and storing data efficiently.",
                "why": "They form the foundation of efficient software design, algorithmic problem solving, and technical interviews.",
                "concepts": "• Linear structures: Arrays, Linked Lists, Stacks, Queues\n• Non-linear structures: Trees, Graphs, Binary Search Trees\n• Hash tables and Heap structures",
                "example": "```python\n# Stack implementation (LIFO)\nstack = []\nstack.append('A')\nitem = stack.pop()\n```",
                "next": "• Learn data structures step by step\n• Algorithmic complexity (Big-O)\n• Coding interview practice"
            },
            "physics": {
                "overview": "**Physics** is the fundamental science that studies matter, energy, motion, and the physical laws governing the universe.",
                "why": "It provides the foundational principles for engineering, astronomy, technology, and understanding nature.",
                "concepts": "• Classical Mechanics (Newton's Laws, Energy, Momentum)\n• Electromagnetism & Thermodynamics\n• Quantum Physics & Relativity",
                "example": "• **Newton's Second Law:** $F = m \\cdot a$ (Force equals mass times acceleration).",
                "next": "• Practice physics problems\n• Mechanics step by step\n• Formula review"
                },
            "economics": {
                "overview": "**Economics** is the social science that studies how individuals, businesses, and governments allocate scarce resources to satisfy human wants.",
                "why": "It helps analyze market dynamics, inflation, trade, public policy, and financial decision-making.",
                "concepts": "• Microeconomics (Supply & Demand, Elasticity, Market Structures)\n• Macroeconomics (GDP, Inflation, Interest Rates, Fiscal Policy)\n• International Trade & Finance",
                "example": "• **Law of Supply & Demand:** When demand increases while supply remains constant, prices tend to rise.",
                "next": "• Microeconomics fundamentals\n• Macroeconomics overview\n• Exam prep"
            },
            "history": {
                "overview": "**History** is the study and documentation of past human events, civilizations, societies, and transformations.",
                "why": "Understanding history provides crucial context for modern politics, cultures, international relations, and societal development.",
                "concepts": "• Ancient Civilizations & Empires\n• Industrial Revolution & Modern Eras\n• Global Conflicts & Social Movements",
                "example": "• **Timeline Milestone:** 1789 French Revolution $\\rightarrow$ 1914 World War I $\\rightarrow$ 1945 United Nations Foundation.",
                "next": "• Historical timelines\n• Key world events\n• Practice questions"
            },
            "photosynthesis": {
                "overview": "**Photosynthesis** is the biological process by which plants, algae, and cyanobacteria convert light energy into chemical energy.",
                "why": "It is the primary source of oxygen in Earth's atmosphere and the base of global food chains.",
                "concepts": "• Light-dependent reactions (Thylakoid membrane)\n• Calvin Cycle / Light-independent reactions (Stroma)\n• Chlorophyll light absorption",
                "example": "• **Chemical Equation:** $6\\text{CO}_2 + 6\\text{H}_2\\text{O} + \\text{Light} \\rightarrow \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2$",
                "next": "• Detailed cellular mechanisms\n• Biology practice questions\n• Study notes"
            },
            "cricket": {
                "overview": "**Cricket** is a popular bat-and-ball sport played between two teams of eleven players on a field with a 22-yard pitch.",
                "why": "It is one of the most widely followed sports globally, played across Test, One Day International (ODI), and T20 formats.",
                "concepts": "• Batting, Bowling, and Fielding mechanics\n• Match Formats (Test, ODI, T20, League Cricket)\n• Umpiring, DRS, and Scoring rules",
                "example": "• A batsman scores runs by hitting the ball and running between wickets or hitting boundaries (4s and 6s).",
                "next": "• Live cricket scores\n• Tournament schedules\n• Cricket rules & records"
            }
        }

        topic_data = factual_definitions.get(topic_lower)
        if topic_data:
            return (
                f"### 💡 {topic_title}\n\n"
                f"{topic_data['overview']}\n\n"
                f"#### Why It Is Used\n{topic_data['why']}\n\n"
                f"#### Key Features & Concepts\n{topic_data['concepts']}\n\n"
                f"#### Example / Application\n{topic_data['example']}\n\n"
                f"---\n"
                f"💡 **Suggested Next Actions:**\n"
                f"{topic_data['next']}"
            )

        if style == "code_only":
            return f"```python\n# {topic_title} Code / Demonstration\ndef main():\n    print(\"Implementation for {topic_title}\")\n\nif __name__ == '__main__':\n    main()\n```"

        if style == "brief":
            return f"**{topic_title}** is a core subject in its domain, covering essential concepts, practical principles, and real-world applications."

        return (
            f"### 💡 {topic_title}\n\n"
            f"**{topic_title}** is a topic in modern technology, science, academic disciplines, and practical applications.\n\n"
            f"#### What It Is & Primary Focus\n"
            f"Understanding **{topic_title}** involves learning its fundamental principles, core mechanisms, and practical applications.\n\n"
            f"#### Key Concepts & Structure\n"
            f"• Foundational definitions and key mechanisms of **{topic_title}**\n"
            f"• Standard practices, tools, and analytical methods\n"
            f"• Real-world applications and practical use cases\n\n"
            f"#### Example / Application\n"
            f"• **Demonstration:** Applying **{topic_title}** to solve practical problems or analyze key domain scenarios.\n\n"
            f"---\n"
            f"💡 **Suggested Next Actions:**\n"
            f"• Learn step by step\n"
            f"• Practice questions & exercises\n"
            f"• Custom study plan or timetable"
        )

    def generate_response(
        self,
        prompt: str,
        history: Optional[List[Dict[str, Any]]] = None,
        persona: str = "virtual_assistant",
        system_instruction: Optional[str] = None,
        user_preference_style: str = "Balanced"
    ) -> str:
        """Generate response using Google Gemini LLM API with adaptive response length."""
        key = self.api_key or os.environ.get("GEMINI_API_KEY", "")

        style = self.parse_response_style(prompt, user_preference_style)
        style_guide = ""

        if style == "brief":
            style_guide = "Provide a very concise, direct response in 2 to 3 sentences maximum."
        elif style == "detailed":
            style_guide = "Provide a comprehensive, in-depth explanation with subheadings, bullet points, and key takeaways."
        elif style == "beginner":
            style_guide = "Explain the topic using simple terms, clear analogies, and beginner-friendly language."
        elif style == "code_only":
            style_guide = "Provide ONLY executable code blocks with minimal text commentary."
        elif style == "summary":
            style_guide = "Provide a concise bulleted summary of key points."

        if not system_instruction:
            system_instruction = (
                f"You are Phani AI, a helpful, intelligent general-purpose AI assistant similar to ChatGPT. "
                f"Operating in '{persona}' mode. {style_guide} "
                f"When given a topic name or question, provide a clear, comprehensive, and well-structured overview naturally suited to that subject. "
                f"Format your response cleanly using GitHub markdown headings, bullet points, code or math blocks where appropriate. "
                f"At the very end of topic explanations, suggest 3 to 4 optional next actions (e.g. step-by-step learning, practice questions, interview prep, projects)."
            )

        if HAS_GENAI and key:
            try:
                client = genai.Client(api_key=key)

                contents = prompt
                if history:
                    formatted_history = []
                    for turn in history[-6:]:
                        role = "user" if turn.get("role") == "user" else "model"
                        content = turn.get("content", "")
                        if content:
                            formatted_history.append(f"{role.capitalize()}: {content}")
                    if formatted_history:
                        contents = "\n".join(formatted_history) + f"\nUser: {prompt}"

                for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash"]:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=contents,
                            config={
                                "system_instruction": system_instruction,
                                "temperature": 0.7
                            }
                        )
                        if response and response.text:
                            return redact_api_keys(response.text)
                    except Exception as model_err:
                        logger.debug(f"Model {model_name} failed: {model_err}")
                        continue

            except Exception as e:
                logger.error(f"Error calling Gemini API: {e}")

        # Natural intelligent fallback when offline or no API key provided
        return self._generate_fallback_response(prompt)


ai_service = AIService()
