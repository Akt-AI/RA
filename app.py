import streamlit as st
import requests
import json
import os
import random
import sqlite3

import streamlit as st
from src.rag_git_web import *
from src.rag_websearch import *
from src.pdf_chat import *
from src.graph_ploter import *
from src.help import *
from src.notes import *
from src.settings import *
from src.models_list import *
# from src.chat import *
# from src.app import * # latest chat


# Configuration
DATABASE_FILE = "user_data.db"
OLLAMA_API_URL = "http://localhost:11434"
HISTORY_DIR = "chat_history"
EMOJI_LIST = ["😀", "🎉", "🤖", "🌟", "🧠", "📚", "💬", "🚀", "📝", "🎨", "✨"]

# Ensure chat history directory exists
os.makedirs(HISTORY_DIR, exist_ok=True)

# Initialize database
def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL,
               password TEXT NOT NULL
           )"""
    )
    conn.commit()
    conn.close()

init_database()

# Initialize session state variables
def init_session_state():
    session_defaults = {
        "chat_history": [],
        "current_chat_file": None,
        "session_emoji": random.choice(EMOJI_LIST),
        "stop_generation": False,
        "is_logged_in": False,
        "current_user": None,
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Authentication Functions
def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Research Assistant")

        username = st.text_input("👤 Username", key="login_username")
        password = st.text_input("🔑 Password", type="password", key="login_password")

        if st.button("✨ Login"):
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                st.session_state.is_logged_in = True
                st.session_state.current_user = username
                st.success("🎉 Logged in successfully!")
            else:
                st.error("❌ Invalid username or password.")

def register():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📝 Register")

        username = st.text_input("👤 Choose a Username", key="register_username")
        password = st.text_input("🔑 Create a Password", type="password", key="register_password")
        confirm_password = st.text_input("🔑 Confirm Your Password", type="password", key="register_confirm_password")

        if st.button("✨ Register"):
            if password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif not username or not password:
                st.error("❌ All fields are required.")
            else:
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    st.success("🎉 Registration successful! You can now log in.")
                except sqlite3.IntegrityError:
                    st.error("❌ Username already exists.")
                conn.close()

# Sidebar Functions
def add_sidebar():
    st.sidebar.title("🌟 RA Settings")

    if st.session_state.is_logged_in:
        st.sidebar.markdown(f"Logged in as: **{st.session_state.current_user}**")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.is_logged_in = False
            st.session_state.current_user = None
            # st.experimental_rerun()

    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        models_list = [model["name"] for model in models]
    except requests.RequestException:
        st.sidebar.error("⚠️ Failed to fetch models.")
        models_list = []

    selected_model = st.sidebar.selectbox("🤖 Select a Model", models_list, index=models_list.index("qwen2.5:0.5b") if "qwen2.5:0.5b" in models_list else 0)
    temperature = st.sidebar.slider("🌡️ Adjust Temperature", 0.0, 1.0, 0.7)

    st.sidebar.header("🗂️ Chat Management")
    if st.sidebar.button("➕ Start New Chat"):
        st.session_state.chat_history = []
        st.session_state.current_chat_file = None
        st.session_state.session_emoji = random.choice(EMOJI_LIST)

    saved_histories = os.listdir(HISTORY_DIR)
    if saved_histories:
        st.sidebar.markdown("### 📂 Load Previous Chats")
        for file_name in saved_histories:
            if st.sidebar.button(f"📄 {file_name}", key=f"load_{file_name}"):
                load_chat_history(file_name)

    if st.sidebar.button("🗑️ Clear All History"):
        for file in os.listdir(HISTORY_DIR):
            os.remove(os.path.join(HISTORY_DIR, file))

    return selected_model, temperature

# Chat and Image Functions
def generate_response(model, prompt, temperature):
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={"model": model, "prompt": prompt, "temperature": temperature, "num_ctx": 8000},
            stream=True
        )
        response.raise_for_status()
        for chunk in response.iter_lines():
            if st.session_state.stop_generation:
                break
            if chunk:
                chunk_data = json.loads(chunk.decode("utf-8"))
                if "response" in chunk_data:
                    yield chunk_data["response"]
    except requests.RequestException as e:
        st.error(f"⚠️ Error during generation: {e}")

def download_image(prompt):
    try:
        response = requests.get(f"https://pollinations.ai/p/{prompt}")
        response.raise_for_status()
        file_name = f"{prompt.replace(' ', '_')}_image.jpg"
        with open(file_name, "wb") as file:
            file.write(response.content)
        return file_name
    except requests.RequestException as e:
        st.error(f"⚠️ Image generation failed: {e}")
        return None

# Chat Management
def save_chat_history():
    if st.session_state.chat_history:
        file_name = f"{st.session_state.session_emoji}_chat.md"
        file_path = os.path.join(HISTORY_DIR, file_name)
        with open(file_path, "w") as file:
            for msg in st.session_state.chat_history:
                file.write(f"**{msg['role'].capitalize()}:** {msg['message']}\n\n")

def load_chat_history(file_name):
    file_path = os.path.join(HISTORY_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            st.session_state.chat_history = [
                {"role": "user", "message": line.replace("**User:**", "").strip()} if "**User:**" in line else
                {"role": "assistant", "message": line.replace("**Assistant:**", "").strip()} for line in file
            ]

# Main Chat
def ra_chat():
    selected_model, temperature = add_sidebar()
    if not selected_model:
        st.warning("⚠️ Please select a model.")
        return

    st.title("💬 Research Assistant")
    st.markdown("Welcome to your intelligent assistant! Start a conversation and explore the possibilities of AI.")
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["message"])

    prompt = st.chat_input("💬 Type your message:")
    col1, col2 = st.columns(2)
    with col1:
        stop_button = st.button("⏹️ Stop", key="stop_button")
    with col2:
        regenerate_button = st.button("🔄 Regenerate", key="regenerate_button")

    if stop_button:
        st.session_state.stop_generation = True

    if regenerate_button and st.session_state.chat_history:
        last_user_prompt = next(
            (msg["message"] for msg in reversed(st.session_state.chat_history) if msg["role"] == "user"), None
        )
        if last_user_prompt:
            st.session_state.chat_history.pop()  # Remove last assistant message
            st.session_state.chat_history.pop()  # Remove last user message
            st.session_state.chat_history.append({"role": "user", "message": last_user_prompt})
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response = ""
                for chunk in generate_response(selected_model, last_user_prompt, temperature):
                    response += chunk
                    response_placeholder.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "message": response})
            save_chat_history()

    if prompt:
        if prompt.startswith("/gen "):
            image_prompt = prompt[5:].strip()
            file_name = download_image(image_prompt)
            if file_name:
                st.image(file_name, caption=f"Generated Image: {image_prompt}")
        else:
            st.session_state.chat_history.append({"role": "user", "message": prompt})
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response = ""
                for chunk in generate_response(selected_model, prompt, temperature):
                    response += chunk
                    response_placeholder.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "message": response})
            save_chat_history()


# Main app with tabs
def main_all():
    # st.set_page_config(page_title="Streamlit Tabs Example", layout="wide")
    chat, tab2, tab3, tab4, tab5, agents, workflows, help, notes, chat_history, settings, models_apis  \
               = st.tabs(["RA", "🔍 Web Search RAG", "📂 GitHub & URL Chat", \
                                      "📄 PDF Chat",  \
                                      "📄 GraphPloter", \
                                      "Agents", \
                                      "Workflows", \
                                      "Help", \
                                      "Notes", \
                                      "Chat History", \
                                      "Settings", \
                                      "Models/APIs", \
                                      ]
                                      )

    
    ## Synthetic Data Generator
    with chat:
        ra_chat()

    with tab2:
        main_websearch()  # Call the first app in the first tab

    with tab3:
        main_rag_git()  # Call the second app in the second tab
    
    with tab4:
        main_pdf_chat()  # Call the second app in the second tab
    
    with tab5:
        main_graph()
    
    with agents:
        pass

    with workflows:
        pass

    with help:
        main_help()

    with notes:
        main_notes()

    with chat_history:
        pass

    with settings:
        main_settings()

    with models_apis:
        main_models_list()

def main():
    st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖", layout="wide")
    if not st.session_state.is_logged_in:
        page = st.sidebar.radio("Navigation", ["Login", "Register"], key="auth_navigation")
        st.sidebar.header("💡 Features")
        st.sidebar.markdown("- AI-powered chat assistant")
        st.sidebar.markdown("- Generate text-based responses")
        st.sidebar.markdown("- Adjust model temperature for creativity")
        st.sidebar.markdown("- Save and load chat history")
        st.sidebar.markdown("- Register and login for a personalized experience")
        st.sidebar.markdown("- [To Know More](https://httpsgithubcomakt-aimydocs.readthedocs.io/en/latest/introduction.html)")
        st.sidebar.markdown("- [Wiki](https://github.com/Akt-AI/MyDocs/wiki)")

        
        
        if page == "Login":
            login()
        elif page == "Register":
            register()
    # elif:
    #     ra_chat()
    else:
        main_all()


# Application Entry Point
if __name__ == "__main__":
    main()
