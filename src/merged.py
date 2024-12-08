import streamlit as st
import requests
import json
import base64
import os
import random

# Configuration
OLLAMA_API_URL = "http://localhost:11434"
TEXT_MODEL = "qwen2.5:0.5b"
IMAGE_MODEL = "llava-phi3"
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)
API_BASE_URL = "http://localhost:5000"

# Emoji list for random selection
EMOJI_LIST = ["😀", "🎉", "🤖", "🌟", "🧠", "📚", "💬", "🚀", "📝", "🎨", "✨"]

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_file" not in st.session_state:
    st.session_state.current_chat_file = None
if "session_emoji" not in st.session_state:
    st.session_state.session_emoji = random.choice(EMOJI_LIST)


def generate_text_response(prompt):
    """Generate a text response using the text model API."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={"model": TEXT_MODEL, "prompt": prompt},
            stream=True,
        )
        if response.status_code == 200:
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = json.loads(chunk.decode("utf-8"))
                        if "response" in chunk_data:
                            yield chunk_data["response"]
                    except json.JSONDecodeError:
                        st.error("Error parsing response chunk.")
        else:
            st.error(f"Error generating text response: {response.text}")
            yield ""
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        yield ""


def generate_image_response(prompt, image_data):
    """Generate a response using the image model API with an image."""
    try:
        encoded_image = base64.b64encode(image_data).decode("utf-8")
        payload = {
            "model": IMAGE_MODEL,
            "prompt": prompt,
            "stream": False,
            "images": [encoded_image],
        }
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=payload,
        )
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("response", "No response received.")
        else:
            st.error(f"Error generating image response: {response.text}")
            return "Error in response."
    except Exception as e:
        st.error(f"Unexpected error during image response generation: {e}")
        return "Error in image response."


def save_chat_history():
    """Save the current chat history to a Markdown file."""
    if not st.session_state.chat_history:
        return

    if not st.session_state.current_chat_file:
        first_prompt = st.session_state.chat_history[0]["message"] if st.session_state.chat_history else "chat"
        sanitized_filename = "".join(c for c in first_prompt if c.isalnum() or c in (" ", "_", "-")).rstrip()
        st.session_state.current_chat_file = f"{st.session_state.session_emoji}_{sanitized_filename[:30].replace(' ', '_')}.md"

    file_path = os.path.join(HISTORY_DIR, st.session_state.current_chat_file)
    with open(file_path, "w") as file:
        file.write(f"# Chat Session {st.session_state.session_emoji}\n\n")
        for msg in st.session_state.chat_history:
            if msg["role"] == "image":
                file.write(f"**{msg['role'].capitalize()}:** [Image Uploaded]\n\n")
            else:
                file.write(f"**{msg['role'].capitalize()}:** {msg['message']}\n\n")


def main():
    st.title("AI Assistant with STT, TTS, and Chat")

    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["🗣️ Speech-to-Text", "📝 Text-to-Speech", "💬 AI Chat"])

    # Speech-to-Text (STT)
    with tab1:
        st.header("Speech-to-Text")
        audio_file = st.file_uploader("Upload an audio file:", type=["wav", "mp3", "m4a"])

        if st.button("Transcribe Audio"):
            if audio_file:
                try:
                    api_url = f"{API_BASE_URL}/transcribe_audio"
                    files = {"file": audio_file}
                    with st.spinner("Transcribing audio..."):
                        response = requests.post(api_url, files=files)

                    if response.status_code == 200:
                        result = response.json()
                        st.success("Transcription Complete!")
                        st.write(f"**Detected Language:** {result['language']}")
                        st.write(f"**Transcription:** {result['transcription']}")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
            else:
                st.warning("Please upload an audio file.")

    # Text-to-Speech (TTS)
    with tab2:
        st.header("Text-to-Speech")
        with st.form("tts_form"):
            model_name = st.selectbox(
                "Select a model:",
                ["gguf", "wisher_tiny"],
                help="Choose between GGUF or Wisher Tiny for speech synthesis.",
            )
            text = st.text_area("Enter text for speech synthesis:", height=150)
            temperature = st.slider("Temperature (stability vs expressiveness)", 0.1, 2.0, 0.1)
            repetition_penalty = st.slider("Repetition Penalty", 0.5, 2.0, 1.1)
            max_length = st.number_input("Maximum Length", min_value=100, max_value=4096, value=4096)

            submitted = st.form_submit_button("Generate Speech")

        if submitted:
            api_url = f"{API_BASE_URL}/generate_tts"
            payload = {
                "text": text,
                "model_name": model_name,
                "temperature": temperature,
                "repetition_penalty": repetition_penalty,
                "max_length": max_length,
            }

            with st.spinner("Generating speech..."):
                response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                output_file = f"{model_name}_output.wav"
                with open(output_file, "wb") as f:
                    f.write(response.content)

                st.audio(output_file, format="audio/wav")
                st.success("Speech synthesis complete!")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

    # AI Chat Assistant
    with tab3:
        st.header("AI Chat Assistant")
        # Sidebar for chat history
        st.sidebar.header("Chat History")
        if st.sidebar.button("➕ New Chat"):
            st.session_state.chat_history = []
            st.session_state.current_chat_file = None
            st.session_state.session_emoji = random.choice(EMOJI_LIST)

        saved_histories = os.listdir(HISTORY_DIR)
        if saved_histories:
            st.sidebar.markdown("### Saved Chats")
            for file_name in saved_histories:
                if st.sidebar.button(f"📄 {file_name}"):
                    with open(os.path.join(HISTORY_DIR, file_name), "r") as file:
                        st.session_state.chat_history = [{"role": "user", "message": line} for line in file.readlines()]

        # Chat input
        uploaded_image = st.file_uploader("Upload an image or type your question:", type=["png", "jpg", "jpeg"])
        prompt = st.chat_input("Type your message:")

        if prompt or uploaded_image:
            with st.chat_message("user"):
                st.markdown(prompt if prompt else "[Image Uploaded]")
                st.session_state.chat_history.append({"role": "user", "message": prompt if prompt else "[Image Uploaded]"})

            with st.chat_message("assistant"):
                if uploaded_image:
                    image_response = generate_image_response(prompt or "Analyze the uploaded image.", uploaded_image.read())
                    st.markdown(image_response)
                else:
                    response_placeholder = st.empty()
                    for chunk in generate_text_response(prompt):
                        response_placeholder.markdown(chunk)

            save_chat_history()


if __name__ == "__main__":
    st.set_page_config(page_title="AI Assistant", layout="wide")
    main()

