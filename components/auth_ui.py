"""
User Authentication UI Component for Phani AI.
Provides Sign In, Registration, Account details, and session management.
"""

import streamlit as st
from database.database import SessionLocal
from auth.authentication import authenticate_user, register_user, get_current_user_dict


def render_auth_modal():
    """Render Sign In / Register dialog in Streamlit sidebar or popup."""
    current_user = get_current_user_dict()

    if st.session_state.get("authenticated", False):
        st.markdown(f"👤 **Logged in as:** `{current_user['username']}` (`{current_user['role'].upper()}`)")
        if st.button("🚪 Log Out"):
            st.session_state.authenticated = False
            st.session_state.current_user = {
                "id": 1,
                "username": "Phani User",
                "email": "user@phani.ai",
                "role": "user"
            }
            st.rerun()
    else:
        with st.expander("🔑 Sign In / Register Account", expanded=False):
            tab_login, tab_register = st.tabs(["Sign In", "Register"])

            with tab_login:
                login_email = st.text_input("Email Address", value="user@phani.ai", key="auth_login_email")
                login_password = st.text_input("Password", type="password", value="password123", key="auth_login_pwd")
                
                if st.button("Sign In"):
                    db = SessionLocal()
                    user = authenticate_user(db, login_email, login_password)
                    db.close()

                    if user:
                        st.session_state.authenticated = True
                        st.session_state.current_user = {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role
                        }
                        st.success(f"Welcome back, {user.username}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

            with tab_register:
                reg_name = st.text_input("Full Name", key="auth_reg_name")
                reg_email = st.text_input("Email Address", key="auth_reg_email")
                reg_pwd = st.text_input("Password", type="password", key="auth_reg_pwd")

                if st.button("Create Account"):
                    if not reg_name or not reg_email or not reg_pwd:
                        st.warning("Please complete all registration fields.")
                    else:
                        db = SessionLocal()
                        user = register_user(db, reg_name, reg_email, reg_pwd, role="user")
                        db.close()

                        if user:
                            st.session_state.authenticated = True
                            st.session_state.current_user = {
                                "id": user.id,
                                "username": user.username,
                                "email": user.email,
                                "role": user.role
                            }
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error("An account with this email already exists.")
