"""
Universal Topic Explanation & Learning Service for Phani AI.
Dynamically explains ANY topic across all knowledge domains, builds learning roadmaps/blocks,
generates custom study timetables, and produces dynamic quizzes with requested question counts.
No hardcoded topic responses.
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from services.ai_service import ai_service

logger = logging.getLogger("PhaniAI.StudentService")


class StudentService:
    def parse_topic_request(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into Topic, Length, Level, and Additional Instructions."""
        q_lower = query.lower()

        # Parse Length
        length = "balanced"
        if any(w in q_lower for w in ["briefly", "brief", "short", "concise", "in short"]):
            length = "brief"
        elif any(w in q_lower for w in ["in detail", "detailed", "comprehensive", "deep dive"]):
            length = "detailed"

        # Parse Level
        level = None
        if any(w in q_lower for w in ["beginner", "easy", "simple", "for a beginner", "for beginners"]):
            level = "beginner"
        elif any(w in q_lower for w in ["intermediate"]):
            level = "intermediate"
        elif any(w in q_lower for w in ["advanced", "expert", "technical", "mathematical"]):
            level = "advanced"

        # Parse Special Instructions
        include_example = any(w in q_lower for w in ["example", "analogy", "real-world", "case study"])

        # Extract Topic cleanly
        topic = re.sub(
            r'(?i)\b(at\s+a\s+(?:beginner|intermediate|advanced|expert)\s+level|at\s+(?:beginner|intermediate|advanced|expert)\s+level|at\s+a\s+level|at\s+level|for\s+(?:a\s+)?(?:beginner|beginners|students|student|freshers|kids)|for\s+an?\s+interview|interview\s+questions|interview\s+answer|interview|create\s+a?\s+timetable\s+for|study\s+plan|schedule|quiz\s+me\s+on|quiz\s+me|quiz|questions|question|only\s+code|code\s+only|with\s+an?\s+example|with\s+examples|step\s+by\s+step|in\s+detail|detailed|briefly|simply|like\s+i\'m\s+\d+|define|definition\s+of|explain|describe|teach\s+me|teach|tell\s+me\s+about|what\s+is|what\s+are|how\s+does|research|compare|latest|current|version)\b',
            '',
            query
        ).strip()
        topic = re.sub(r'(?i)\b(beginner|beginners|intermediate|advanced|expert|level|levels|brief|short|concise)\b', '', topic).strip()
        topic = topic.strip("'\"")
        topic = re.sub(r'^[^\w]+|[^\w]+$', '', topic).strip()
        topic = topic.strip("'\"")

        formatted_topic = topic
        if topic.isupper():
            formatted_topic = topic
        elif len(topic) > 0:
            formatted_topic = topic[0].upper() + topic[1:]
        else:
            formatted_topic = query.strip("'\"")

        return {
            "topic": formatted_topic,
            "length": length,
            "level": level,
            "include_example": include_example,
            "raw_query": query
        }

    def explain_topic(
        self,
        topic_query: str,
        target_level: Optional[str] = None,
        length_style: Optional[str] = None,
        include_examples: bool = True
    ) -> str:
        """Dynamically generate explanation for ANY topic across all knowledge domains."""
        parsed = self.parse_topic_request(topic_query)
        topic_name = parsed["topic"] if parsed["topic"] else topic_query.strip("'\"")
        effective_level = target_level or parsed["level"] or "standard"
        effective_length = length_style or parsed["length"] or "balanced"

        example_instruction = "Include at least one clear real-world example or analogy to illustrate the concept." if (include_examples or parsed["include_example"]) else ""
        level_str = f" for a {effective_level} level audience" if effective_level != "standard" else ""

        instruction = (
            f"You are a master professor and general-purpose knowledge expert AI. "
            f"Explain the concept of '{topic_name}'{level_str}. "
            f"Length requirement: {effective_length.upper()}. {example_instruction} "
            f"Format your response clearly using GitHub markdown, bold headings, bullet points, and code/math blocks where appropriate."
        )

        response = ai_service.generate_response(
            prompt=f"Explain {topic_name}",
            system_instruction=instruction
        )

        if response:
            return response

        # Dynamic fallback explanation generator
        example_block = ""
        if include_examples or parsed["include_example"]:
            example_block = f"• **Real-World Example:** Applying **{topic_name}** to practical scenarios and real-world domain problem solving.\n"

        return (
            f"### 💡 {topic_name}\n\n"
            f"**{topic_name}** is a core subject covering key mechanisms, practical tools, and analytical principles.\n\n"
            f"• **Key Principle:** Foundational mechanisms defining **{topic_name}**.\n"
            f"{example_block}"
            f"• **Practical Applications:** Widely applied across software engineering, research, education, and industry."
        )

    def generate_dynamic_quiz_by_query(self, query: str) -> Tuple[List[Dict[str, Any]], int]:
        """Extract requested question count (e.g. 10, 20, 30) and generate dynamic quiz questions."""
        # Extract requested number of questions
        count_match = re.search(r'\b(\d+)\s*(?:questions|question|qs|q|mcqs)\b', query, re.IGNORECASE)
        num_questions = int(count_match.group(1)) if count_match else 5
        num_questions = min(max(num_questions, 1), 30)

        # Extract topic from query
        topic = re.sub(r'(?i)\b(give me|generate|create|\d+|questions|question|about|on|for|quiz)\b', '', query).strip() or "General Knowledge"

        instruction = (
            f"You are an expert exam creator AI. Generate exactly {num_questions} multiple choice practice questions for '{topic}'. "
            f"Respond with ONLY a JSON array of objects with keys: 'question', 'options' (array of 4 strings), 'answer' (string), 'explanation' (string)."
        )

        ai_res = ai_service.generate_response(
            prompt=f"Generate {num_questions} practice quiz questions for '{topic}' in JSON format.",
            system_instruction=instruction
        )

        if ai_res:
            try:
                json_match = re.search(r'\[.*\]', ai_res, re.DOTALL)
                if json_match:
                    quizzes = json.loads(json_match.group(0))
                    if isinstance(quizzes, list) and len(quizzes) > 0:
                        return quizzes, len(quizzes)
            except Exception as e:
                logger.error(f"Error parsing dynamic quiz JSON: {e}")

        # Dynamic fallback questions generator
        quizzes = []
        for i in range(1, num_questions + 1):
            quizzes.append({
                "question": f"Q{i}: What is key concept #{i} regarding {topic.capitalize()}?",
                "options": [
                    f"A) Core principle {i} of {topic.capitalize()}",
                    "B) Unrelated concept",
                    "C) Secondary auxiliary property",
                    "D) None of the above"
                ],
                "answer": f"A) Core principle {i} of {topic.capitalize()}",
                "explanation": f"This tests understanding of concept #{i} in {topic.capitalize()}."
            })
        return quizzes, num_questions

    def generate_quiz(self, topic: str = "General Science") -> List[Dict[str, Any]]:
        quizzes, _ = self.generate_dynamic_quiz_by_query(f"5 questions about {topic}")
        return quizzes

    def generate_roadmap_and_lesson(self, query: str) -> str:
        """Break subject into logical learning blocks dynamically for ANY requested subject."""
        topic = re.sub(r'(?i)\b(teach me|completely|step by step|roadmap|learning blocks|lesson|explain)\b', '', query).strip() or "the requested subject"

        instruction = (
            f"You are a master educator AI. Break down '{topic}' into a complete step-by-step learning roadmap with logical learning blocks. "
            f"Provide a clear roadmap outline, then explain Block 1 in detail with Concept, Simple Explanation, Terminology, Examples, and Practice Question."
        )

        res = ai_service.generate_response(
            prompt=f"Teach me {topic} completely step by step.",
            system_instruction=instruction
        )

        if res:
            return res

        return (
            f"### 📚 Learning Roadmap: {topic.capitalize()}\n\n"
            f"**Block 1 — Introduction & Fundamentals**\n"
            f"• **Concept:** Core definitions and foundational principles of {topic.capitalize()}.\n"
            f"• **Simple Explanation:** Understand the basic building blocks before moving into advanced topics.\n"
            f"• **Terminology:** Key terms, definitions, and essential syntax/formulae.\n"
            f"• **Example:** Practical real-world application of {topic.capitalize()}.\n\n"
            f"**Block 2 — Core Operations & Syntax / Rules**\n"
            f"**Block 3 — Advanced Concepts & Practical Projects**\n"
            f"**Block 4 — Interview & Exam Preparation**\n\n"
            f"*(Type 'Next block' or 'Start Block 2' to continue learning!)*"
        )

    def generate_study_timetable(self, query: str) -> str:
        """Dynamically generate custom study timetable/plan based on user parameters."""
        instruction = (
            f"You are an expert study planner AI. Generate a structured, realistic study plan / timetable based on the user's request: '{query}'. "
            f"Include daily/weekly milestones, recommended study hours, revision blocks, and practice sessions."
        )

        res = ai_service.generate_response(
            prompt=f"Create a study plan for: {query}",
            system_instruction=instruction
        )

        if res:
            return res

        return (
            f"### 📅 Custom Study Plan & Timetable\n\n"
            f"**Overview for:** *\"{query}\"*\n\n"
            f"| Phase | Duration | Core Focus | Daily Allocation |\n"
            f"| :--- | :--- | :--- | :--- |\n"
            f"| **Phase 1: Foundations** | Days 1–7 | Core concepts & definitions | 2 hours/day |\n"
            f"| **Phase 2: Practice** | Days 8–20 | Problem solving & exercises | 2.5 hours/day |\n"
            f"| **Phase 3: Revision** | Days 21–30 | Mock exams & interview prep | 2 hours/day |\n\n"
            f"💡 **Study Advice:** Maintain consistency, schedule 10-minute breaks every hour, and review past notes weekly."
        )

    def generate_sql_practice(self, level: str = "Intermediate") -> str:
        return self.generate_roadmap_and_lesson(f"SQL {level} practice questions")


student_service = StudentService()
