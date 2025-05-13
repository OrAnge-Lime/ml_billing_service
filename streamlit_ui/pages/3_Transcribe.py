# streamlit_ui/pages/3_Transcribe.py
import streamlit as st
import pandas as pd # For potential model display

st.set_page_config(page_title="Transcribe Audio", page_icon="🎧")

from api_client import get_available_models, transcribe_audio, get_user_credits

st.title("🎧 Audio Transcription")

# --- Authentication Check ---
if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this page.")
    st.stop()

# --- Display User Credits ---
# Fetch latest credits when the page loads or after transcription
current_credits = get_user_credits()
if current_credits is not None:
    st.session_state.user_info['credits'] = current_credits # Update session state
    st.metric(label="💰 Your Credits", value=current_credits)
else:
     st.warning("Could not fetch credit balance.")

st.markdown("---")

# --- Model Selection ---
st.subheader("1. Select ASR Model")
models_list = get_available_models()
print(models_list)
model_options = {} # Dictionary to map display name to identifier

if models_list:
    for model in models_list:
        # Assuming model['name'] is user-friendly and model['filename'] has the identifier
        display_name = f"{model.get('name', 'Unnamed Model')} (Cost: {model.get('cost', '?')} credits)"
        identifier = model.get('name') # This should be "whisper-small", etc.
        if identifier:
            model_options[display_name] = identifier
    selected_model_display_name = st.selectbox(
        f"Choose a model: {len(models_list)}",
        options=list(model_options.keys()),
        index=0 # Default selection
    )
    selected_model_identifier = model_options.get(selected_model_display_name)
else:
    st.error("Could not load available models from the API.")
    selected_model_identifier = None


# --- Audio Upload ---
st.subheader("2. Upload Audio File")
uploaded_file = st.file_uploader(
    "Choose an audio file (e.g., mp3, wav, m4a)...",
    type=["mp3", "wav", "m4a", "ogg", "flac", "mpeg", "mp4"] # Common audio types Whisper handles
)

# --- ASR Options ---
st.subheader("3. Transcription Options (Optional)")
col1, col2 = st.columns(2)
with col1:
    language_code = st.text_input("Language Code (e.g., 'en', 'es')", help="Leave blank for auto-detection.")
with col2:
    task = st.selectbox("Task", ["transcribe", "translate"], index=0, help="'translate' will translate to English.")


st.markdown("---")

# --- Submit ---
st.subheader("4. Transcribe!")
transcribe_button = st.button("✨ Start Transcription", type="primary", disabled=(not uploaded_file or not selected_model_identifier))

if transcribe_button:
    if uploaded_file is not None and selected_model_identifier:
        st.info(f"Processing '{uploaded_file.name}' with model '{selected_model_identifier}'...")
        bytes_data = uploaded_file.getvalue()
        content_type = uploaded_file.type
        filename = uploaded_file.name

        with st.spinner("Transcription in progress... Please wait."):
            result_data = transcribe_audio(
                model_identifier=selected_model_identifier,
                audio_file_bytes=bytes_data,
                filename=filename,
                content_type=content_type,
                language=language_code if language_code else None, # Pass None if blank
                task=task
            )

        if result_data:
            st.success("Transcription Process Completed!")
            prediction_status = result_data.get("status_of_prediction")
            transcribed_text = result_data.get("result")
            message = result_data.get("message")

            if prediction_status == "success" and transcribed_text is not None:
                 st.subheader("📄 Transcription Result:")
                 st.text_area("Text", transcribed_text, height=200)
                 # Refresh credits display
                 new_credits = get_user_credits()
                 if new_credits is not None:
                     st.session_state.user_info['credits'] = new_credits
                     st.metric(label="💰 Credits Remaining", value=new_credits)
                 st.balloons()
            else:
                 st.error(f"Transcription failed: {message or 'Unknown reason.'}")
        else:
            # Error message already shown by api_client if network/API error occurred
            pass # api_client handles st.error

    else:
        st.warning("Please select a model and upload an audio file.")