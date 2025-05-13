# streamlit_ui/api_client.py
import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import logging
import os

logger = logging.getLogger(__name__)

# --- Configuration ---
# Prioritize environment variable set by Docker Compose for the API URL
# Fallback to localhost if the variable is not set (for local UI dev outside Docker)
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
# Construct BASE_URL based on environment variables
BASE_URL = f"http://{API_HOST}:{API_PORT}/api/v1"

# Log the final URL being used
logger.info(f"API Client configured to use BASE_URL: {BASE_URL}")
st.sidebar.caption(f"API: {BASE_URL}") # Show in UI for debugging

# --- Helper Functions ---
def get_auth_headers() -> Optional[Dict[str, str]]:
    """Retrieves authentication headers from session state."""
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return None

def handle_response(response: requests.Response, expected_status: int = 200) -> Optional[Dict[str, Any]]:
    """Checks response status and returns JSON data or logs error."""
    if response.status_code == expected_status:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(f"API response decode error for {response.url}. Status: {response.status_code}. Content: {response.text[:100]}")
            st.error("Failed to decode API response.")
            return None
    else:
        try:
            error_data = response.json()
            detail = error_data.get("detail", "No specific error detail provided.")
            # Handle cases where detail might be a list (like validation errors)
            if isinstance(detail, list):
                 detail_str = "; ".join([f"{err.get('loc', ['unknown'])[1]}: {err.get('msg', 'error')}" for err in detail])
                 message = f"API Error ({response.status_code}): {detail_str}"
            elif isinstance(detail, str):
                 message = f"API Error ({response.status_code}): {detail}"
            else:
                 message = f"API Error ({response.status_code}): {response.text[:150]}"

            logger.error(f"API call to {response.url} failed. Status: {response.status_code}. Response: {response.text[:150]}")
            st.error(message)

        except requests.exceptions.JSONDecodeError:
             message = f"API Error ({response.status_code}): {response.text[:150]}"
             logger.error(f"API call to {response.url} failed. Status: {response.status_code}. Content: {response.text[:150]}")
             st.error(message)

        return None


# --- API Functions ---
def login_user(username: str, password: str) -> Optional[str]:
    """Logs in a user and returns the auth token."""
    login_url = f"{BASE_URL}/users/token"
    data = {"username": username, "password": password} # Needs x-www-form-urlencoded
    try:
        response = requests.post(login_url, data=data) # Use data for form encoding
        data = handle_response(response, 200)
        if data and "access_token" in data:
            return data["access_token"]
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error during login: {e}")
        logger.error(f"Network error connecting to {login_url}: {e}")
        return None

def register_user(username: str, password: str) -> bool:
    """Registers a new user."""
    register_url = f"{BASE_URL}/users/register"
    payload = {"username": username, "password": password}
    try:
        response = requests.post(register_url, json=payload)
        data = handle_response(response, 201) # Expect 201 Created
        return data is not None # Return True if registration was successful (got data back)
    except requests.exceptions.RequestException as e:
        st.error(f"Network error during registration: {e}")
        logger.error(f"Network error connecting to {register_url}: {e}")
        return False

def get_user_me() -> Optional[Dict[str, Any]]:
    """Fetches details for the currently logged-in user."""
    me_url = f"{BASE_URL}/users/me"
    headers = get_auth_headers()
    if not headers:
        st.error("Not authenticated.")
        return None
    try:
        response = requests.get(me_url, headers=headers)
        return handle_response(response, 200)
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching user details: {e}")
        logger.error(f"Network error connecting to {me_url}: {e}")
        return None

def get_user_credits() -> Optional[int]:
    """Fetches the current user's credit balance."""
    credits_url = f"{BASE_URL}/users/me/credits"
    headers = get_auth_headers()
    if not headers:
        st.error("Not authenticated.")
        return None
    try:
        response = requests.get(credits_url, headers=headers)
        data = handle_response(response, 200)
        if data and "credits" in data:
            return data["credits"]
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching credits: {e}")
        logger.error(f"Network error connecting to {credits_url}: {e}")
        return None

def get_available_models() -> Optional[List[Dict[str, Any]]]:
    """Fetches the list of available ML models."""
    models_url = f"{BASE_URL}/models/"
    headers = get_auth_headers()
    logger.info(f'Try to fetch models list: {models_url}')
    logger.info(f'Headers: {headers}')
    if not headers:
        st.error("Not authenticated.")
        return None
    try:
        response = requests.get(models_url, headers=headers)
        models_list = handle_response(response, 200)
        return  models_list
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        logger.error(f"Error connecting to {models_url}: {e}")
        return None

def transcribe_audio(
    model_identifier: str, # This is the string like "whisper-small"
    audio_file_bytes: bytes,
    filename: str,
    content_type: str,
    language: Optional[str] = None,
    task: Optional[str] = "transcribe"
) -> Optional[Dict[str, Any]]:
    """Sends audio for transcription."""
    transcribe_url = f"{BASE_URL}/predict/{model_identifier}/transcribe" # Pass identifier in URL
    headers = get_auth_headers()
    if not headers:
        st.error("Not authenticated.")
        return None

    files = {'audio_file': (filename, audio_file_bytes, content_type)}
    data = {} # Form data
    if language:
        data['language'] = language
    if task:
        data['task'] = task

    try:
        logger.info(f"Sending transcription request to {transcribe_url} for model {model_identifier}")
        response = requests.post(transcribe_url, headers=headers, files=files, data=data)
        # Transcription endpoint might return 200 OK even if transcription itself failed internally
        # The payload's 'status_of_prediction' indicates the actual outcome.
        return handle_response(response, 200) # Expect 200 OK from the controller
    except requests.exceptions.RequestException as e:
        st.error(f"Network error during transcription: {e}")
        logger.error(f"Network error connecting to {transcribe_url}: {e}")
        return None

def get_prediction_history(limit: int = 100, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
    """Fetches the user's prediction history."""
    history_url = f"{BASE_URL}/predict/history?limit={limit}&offset={offset}"
    headers = get_auth_headers()
    if not headers:
        st.error("Not authenticated.")
        return None
    try:
        response = requests.get(history_url, headers=headers)
        return handle_response(response, 200) # Returns a list of predictions
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching history: {e}")
        logger.error(f"Network error connecting to {history_url}: {e}")
        return None