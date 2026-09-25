"""
History & Saved Items Manager Component for Phani AI.
Allows browsing chat sessions, viewing message history, renaming/deleting chats, and managing saved items.
"""

import streamlit as st
from database.database import SessionLocal
from database.repositories import ConversationRepository, SavedItemsRepository


def render_history_page():
    st.title("🕘 Phani AI — History & Saved Items")
    st.caption("Manage chat history sessions, saved notes, code snippets, and exported items.")

    tab1, tab2 = st.tabs(["💬 Chat Sessions History", "⭐ Saved Items"])

    db = SessionLocal()
    try:
        with tab1:
            convs = ConversationRepository.list_recent_conversations(db)
            if not convs:
                st.info("No saved chat history yet.")
            else:
                for c in convs:
                    with st.expander(f"💬 {c['title']} ({c['msg_count']} messages) — {c['updated_at'][:10]}", expanded=False):
                        msgs = ConversationRepository.get_conversation_history(db, c['id'])
                        for m in msgs:
                            st.markdown(f"**{m['role'].capitalize()}:** {m['content']}")
                        
                        col_r, col_d = st.columns(2)
                        with col_r:
                            new_title = st.text_input("Rename Chat", value=c['title'], key=f"rename_{c['id']}")
                            if st.button("Save Title", key=f"btn_rename_{c['id']}"):
                                ConversationRepository.rename_conversation(db, c['id'], new_title)
                                st.success("Renamed!")
                                st.rerun()
                        with col_d:
                            if st.button("Delete Chat Session", key=f"del_{c['id']}"):
                                ConversationRepository.delete_conversation(db, c['id'])
                                st.success("Deleted!")
                                st.rerun()

        with tab2:
            items = SavedItemsRepository.list_items(db)
            if not items:
                st.caption("No items saved yet.")
            else:
                for item in items:
                    with st.expander(f"📌 {item.title} ({item.item_type})", expanded=False):
                        st.markdown(item.content)
                        if st.button("Delete Item", key=f"del_item_{item.id}"):
                            SavedItemsRepository.delete_item(db, item.id)
                            st.success("Item Deleted!")
                            st.rerun()
    finally:
        db.close()
