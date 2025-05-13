# streamlit_ui/pages/1_Login.py
import streamlit as st
st.set_page_config(page_title="Login - ASR Service", page_icon="🔑")

from api_client import login_user, get_user_me, get_user_credits # Import necessary functions


st.title("🔑 User Login")

# Redirect if already logged in (or show minimal message)
if st.session_state.get("logged_in", False):
    st.success("You are already logged in!")
    st.stop() # Stop execution for this page

# Login Form
with st.form("login_form"):
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    submitted = st.form_submit_button("Login")

    if submitted:
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            with st.spinner("Attempting login..."):
                token = login_user(username, password)

                if token:
                    st.session_state.auth_token = token
                    st.session_state.logged_in = True

                    # Fetch user details after successful login
                    user_details = get_user_me()
                    credits = get_user_credits() # Get initial credits

                    if user_details:
                        st.session_state.user_info = {
                            "username": user_details.get("username"),
                            "id": user_details.get("id"),
                            "credits": credits if credits is not None else "N/A" # Store credits
                        }
                        st.success("Login successful! Redirecting...")
                        # Use st.rerun() to update the UI state and sidebar
                        # Users can then navigate to other pages
                        st.rerun()
                    else:
                        # Handle case where login succeeded but fetching details failed
                        st.session_state.logged_in = False # Log back out
                        st.session_state.auth_token = None
                        st.error("Login succeeded but failed to fetch user details. Please try again.")
                else:
                    # Error message is handled by login_user() using st.error
                    pass # Error already displayed by api_client

st.markdown("---")
st.caption("Don't have an account? Go to the **Register** page.")