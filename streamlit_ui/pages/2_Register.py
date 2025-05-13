# streamlit_ui/pages/2_Register.py
import streamlit as st
st.set_page_config(page_title="Register - ASR Service", page_icon="📝")

from api_client import register_user

st.title("📝 New User Registration")

if st.session_state.get("logged_in", False):
    st.info("You are already logged in. Logout first to register a new account.")
    st.stop()

with st.form("register_form"):
    reg_username = st.text_input("Choose Username", key="reg_username")
    reg_password = st.text_input("Choose Password", type="password", key="reg_password")
    reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
    reg_submitted = st.form_submit_button("Register")

    if reg_submitted:
        if not reg_username or not reg_password:
            st.warning("Please enter both username and password.")
        elif reg_password != reg_password_confirm:
            st.warning("Passwords do not match.")
        else:
            with st.spinner("Registering..."):
                success = register_user(reg_username, reg_password)
                if success:
                    st.success("Registration successful! You can now log in.")
                    # Optionally clear form fields or navigate/prompt login
                else:
                    # Error message is handled by register_user() using st.error
                    pass # Error already displayed by api_client

st.markdown("---")
st.caption("Already have an account? Go to the **Login** page.")