"""
Universal Topic Explanation & AI Student Assistant UI Component for Phani AI.
Provides single flexible interaction 'Ask Phani AI anything' for topic learning, complete subject roadmaps,
dynamic quizzes, timetable generation, and interview preparation across any domain.
"""

import streamlit as st
from services.student_service import student_service


def render_student_page():
    st.title("🎓 Phani AI — Student & Learning Assistant")
    st.caption("Ask Phani AI to teach any subject step-by-step, generate dynamic quizzes, build custom study timetables, or prepare for interviews.")

    st.markdown("### Ask Phani AI anything")

    # Single flexible interaction input
    user_learning_query = st.text_input(
        "Ask anything — programming, science, math, career, current information, movies, or any other topic...",
        value="",
        placeholder="e.g. 'Python', 'Teach me SQL step by step', 'Physics', 'Create a 30-day study plan'",
        key="student_learning_input"
    )

    col_btn, col_opt = st.columns([1, 4])
    with col_btn:
        btn_submit = st.button("🚀 Start Learning / Practice", type="primary", use_container_width=True)

    st.markdown("---")
    st.write("💡 **Example Requests:**")
    st.caption("• *\"Teach me Python step by step\"* | • *\"Give me 20 questions about physics\"* | • *\"Create a 30-day study plan for exams\"* | • *\"Give me 10 interview questions on data structures\"*")

    if btn_submit and user_learning_query.strip():
        query_text = user_learning_query.strip()
        q_lower = query_text.lower()

        # 1. Quiz Request
        if "quiz" in q_lower or "questions" in q_lower or "question" in q_lower:
            with st.spinner(f"Generating practice questions for '{query_text}'..."):
                quizzes, num_qs = student_service.generate_dynamic_quiz_by_query(query_text)
                st.markdown(f"### 🧩 Practice Quiz ({num_qs} Questions)")
                for idx, q in enumerate(quizzes, 1):
                    st.markdown(f"#### Question {idx}: {q['question']}")
                    for opt in q["options"]:
                        st.write(opt)
                    with st.expander(f"Show Answer & Explanation for Q{idx}"):
                        st.success(f"**Answer:** {q['answer']}")
                        st.write(f"**Explanation:** {q['explanation']}")

        # 2. Complete Subject Learning / Roadmap
        elif any(w in q_lower for w in ["completely", "step by step", "roadmap", "learning blocks", "teach me"]):
            with st.spinner(f"Building learning roadmap & lesson for '{query_text}'..."):
                roadmap_text = student_service.generate_roadmap_and_lesson(query_text)
                st.markdown(roadmap_text)

        # 3. Timetable / Study Plan
        elif any(w in q_lower for w in ["timetable", "study plan", "schedule", "revision", "study timetable"]):
            with st.spinner(f"Generating custom study timetable for '{query_text}'..."):
                timetable_text = student_service.generate_study_timetable(query_text)
                st.markdown(timetable_text)

        # 4. General Topic Explanation
        else:
            with st.spinner(f"Phani AI Explaining '{query_text}'..."):
                explanation = student_service.explain_topic(query_text)
                st.markdown(explanation)
