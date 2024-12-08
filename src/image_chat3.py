import streamlit as st
import requests
import json
import base64
import uuid
import os
import random

OLLAMA_API_URL = "http://localhost:11434"
TEXT_MODEL = "qwen2.5:0.5b"
IMAGE_MODEL = "llava-phi3"

# Ensure chat history directory exists
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

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


def load_chat_history(file_name):
    """Load a saved chat history from the chat_history folder."""
    file_path = os.path.join(HISTORY_DIR, file_name)
    with open(file_path, "r") as file:
        chat_lines = file.readlines()

    st.session_state.chat_history = []
    for line in chat_lines:
        if line.startswith("**User:**"):
            st.session_state.chat_history.append({"role": "user", "message": line.replace("**User:**", "").strip()})
        elif line.startswith("**Assistant:**"):
            st.session_state.chat_history.append({"role": "assistant", "message": line.replace("**Assistant:**", "").strip()})
        elif line.startswith("**Image:**"):
            st.session_state.chat_history.append({"role": "image", "message": "[Image Uploaded]"})

    st.session_state.current_chat_file = file_name


def clear_chat():
    """Clear the chat history and reset session state."""
    st.session_state.chat_history = []
    st.session_state.current_chat_file = None
    st.session_state.session_emoji = random.choice(EMOJI_LIST)


def main_chat():
    st.title("💬 AI Chat Assistant with Enhanced Image Input")

    # Sidebar: Directory tree and new chat button
    st.sidebar.header("Chat History")
    if st.sidebar.button("➕ New Chat"):
        clear_chat()

    saved_histories = os.listdir(HISTORY_DIR)
    if saved_histories:
        st.sidebar.markdown("### Saved Chats")
        for file_name in saved_histories:
            if st.sidebar.button(f"📄 {file_name}"):
                load_chat_history(file_name)

    # Display chat messages from history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            if chat["role"] == "image":
                st.markdown("![Image Uploaded](path/to/image)")  # Placeholder for image visualization
            else:
                st.markdown(chat["message"])

    st.markdown(f"### Current Chat Emoji: {st.session_state.session_emoji}")

    # Chat input
    uploaded_image = st.file_uploader("Upload an image or type your question:", type=["png", "jpg", "jpeg"])
    prompt = st.chat_input("Type your message:")

    if prompt or uploaded_image:
        with st.chat_message("user"):
            if prompt:
                st.markdown(prompt)
                st.session_state.chat_history.append({"role": "user", "message": prompt})
            if uploaded_image:
                st.image(uploaded_image)
                st.session_state.chat_history.append({"role": "image", "message": "[Image Uploaded]"})

        with st.chat_message("assistant"):
            if uploaded_image:
                image_response = generate_image_response(prompt or "Analyze the uploaded image.", uploaded_image.read())
                st.markdown(image_response)
                st.session_state.chat_history.append({"role": "assistant", "message": image_response})
            else:
                response_placeholder = st.empty()
                full_response = ""
                for chunk in generate_text_response(prompt):
                    full_response += chunk
                    response_placeholder.markdown(full_response)
                st.session_state.chat_history.append({"role": "assistant", "message": full_response})

        save_chat_history()


if __name__ == "__main__":
    st.set_page_config(page_title="AI Chat Assistant", layout="wide")
    main_chat()

