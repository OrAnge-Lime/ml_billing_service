# streamlit_ui/ui_main.py
import streamlit as st
import logging

# --- Page Configuration (Set Title, Icon) ---
# This should be the first Streamlit command
st.set_page_config(
    page_title="ASR Billing Service",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging for Streamlit app (optional but good practice)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - UI - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Initialize Session State ---
# Use st.session_state to store login status, token, user info
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None # Store username, credits, etc.
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login" # Default page

# --- Sidebar Navigation and User Info ---
st.sidebar.title("🎙️ ASR Service")

if st.session_state.logged_in and st.session_state.user_info:
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"👤 Welcome, {st.session_state.user_info.get('username', 'User')}!")
    st.sidebar.metric(label="💰 Credits", value=f"{st.session_state.user_info.get('credits', 'N/A')}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        # Clear session state on logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        st.rerun() # Rerun to reflect logged-out state

else:
    st.sidebar.info("Please log in or register using the pages below.")


# --- Main Content Area Guidance ---
st.title("Welcome to the ASR Billing Service UI")

if not st.session_state.logged_in:
    st.info("👈 Please use the sidebar navigation to log in or register.")
    st.markdown("""
    ### Available Pages:
    - **Login:** Access your account.
    - **Register:** Create a new account.
    """)
else:
    st.success("You are logged in! 🎉")
    st.info("👈 Use the sidebar to navigate to **Transcribe** or your **Profile**.")

# Add footer or other common elements if needed
st.markdown("---")
st.caption("Streamlit UI for FastAPI ASR Service")

logger.info(f"Main page loaded. Logged in: {st.session_state.logged_in}")

# Note: The actual page content (Login form, Transcribe form, etc.)
# is handled by the files in the `pages/` directory. Streamlit automatically
# uses the filenames (without the number prefix and `.py`) as the page names
# in the sidebar navigation when st.session_state.logged_in is True.