# EMBEDDING_MODEL = "mxbai-embed-large:latest"

import streamlit as st
import os
import pickle
import numpy as np
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document  # For handling Word documents
import requests
import json

# Default file paths
INDEX_DIR = "indices"
os.makedirs(INDEX_DIR, exist_ok=True)
OLLAMA_API_URL = "http://localhost:11434"
# EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_MODEL = "mxbai-embed-large:latest"

GENERATION_MODEL = "qwen2.5:0.5b"

# Helper function to get a list of available indices
def get_indices():
    return [f.split(".")[0] for f in os.listdir(INDEX_DIR) if f.endswith(".pkl")]

# Step 1: Load Text Data from Files
def load_text_from_file(file):
    """Extract text from uploaded files (PDF, Word, Text)."""
    file_extension = file.name.split('.')[-1].lower()
    extracted_text = ""

    if file_extension == "pdf":
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + " "
    elif file_extension == "docx":
        doc = Document(file)
        for paragraph in doc.paragraphs:
            if paragraph.text:
                extracted_text += paragraph.text + " "
    elif file_extension == "txt":
        extracted_text = file.read().decode("utf-8")
    else:
        st.error(f"Unsupported file type: {file_extension}")
        return None

    return extracted_text.strip()

# Step 2: Generate Embedding
def generate_embedding(text):
    response = requests.post(
        f"{OLLAMA_API_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text}
    )
    if response.status_code == 200:
        return response.json().get("embedding", [])
    else:
        st.error(f"Error generating embedding: {response.text}")
        return None

# Step 3: Index Data
def index_data(data, index_name):
    """Index data using embedding model."""
    collection = {"embeddings": [], "documents": [], "metadata": []}
    st.info("Indexing data...")

    for path, content in data.items():
        embedding = generate_embedding(content)
        if embedding:
            collection["embeddings"].append(embedding)
            collection["documents"].append(content)
            collection["metadata"].append({"path": path})

    with open(os.path.join(INDEX_DIR, f"{index_name}.pkl"), "wb") as f:
        pickle.dump(collection, f)
    st.success(f"Index '{index_name}' saved.")

# Step 4: Query Index
def query_index(prompt, collection):
    """Query the indexed data using embedding model."""
    query_embedding = generate_embedding(prompt)
    if not query_embedding:
        return None, None

    similarities = []
    for embedding in collection["embeddings"]:
        similarity = np.dot(query_embedding, embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
        )
        similarities.append(similarity)

    if similarities:
        max_index = np.argmax(similarities)
        return collection["documents"][max_index], collection["metadata"][max_index]["path"]
    else:
        st.info("The index is empty.")
        return None, None

# Step 5: Load an Existing Index
def load_index(index_name):
    try:
        with open(os.path.join(INDEX_DIR, f"{index_name}.pkl"), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error(f"Index '{index_name}' not found.")
        return None

# Step 6: Generate Response with Streaming
def generate_response(prompt):
    response = requests.post(
        f"{OLLAMA_API_URL}/api/generate",
        json={"model": GENERATION_MODEL, "prompt": prompt},
        stream=True
    )
    if response.status_code == 200:
        response_text = ""
        for chunk in response.iter_lines():
            if chunk:
                try:
                    chunk_data = json.loads(chunk.decode('utf-8'))
                    if "response" in chunk_data:
                        response_text += chunk_data["response"]
                        yield response_text
                except json.JSONDecodeError:
                    st.error("Error parsing response chunk.")
    else:
        st.error(f"Error generating response: {response.text}")
        yield ""

# Streamlit App for Document Upload, Indexing, and Chat
def main_pdf_chat():
    # st.set_page_config(page_title="Document Upload and Chat", page_icon="📄")
    # st.title("📄 Document Upload, Indexing, and Chat")
    # st.sidebar.header("")

    # Tabs for functionality
    tab1, tab2 = st.tabs(["📁 Upload and Index", "💬 Query and Chat"])

    # Tab 1: Upload and Index
    with tab1:
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader("Upload PDF, Word, or Text files", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        index_name = st.text_input("Index Name:", placeholder="Enter a unique name for this index")

        if st.button("Index Documents"):
            if uploaded_files and index_name:
                data = {}
                for file in uploaded_files:
                    text = load_text_from_file(file)
                    if text:
                        data[file.name] = text
                
                index_data(data, index_name)
            else:
                st.warning("Please upload files and provide an index name.")

    # Tab 2: Query and Chat
    with tab2:
        st.subheader("Query Indexed Data")
        indices = get_indices()

        if indices:
            selected_index = st.selectbox("Select an Index", indices, key="pdf_chat")
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_query = st.chat_input("Enter your query:")
            if user_query:
                st.session_state.messages.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)

                collection = load_index(selected_index)
                if collection:
                    retrieved_data, file_path = query_index(user_query, collection)
                    if retrieved_data:
                        with st.chat_message("assistant"):
                            response_placeholder = st.empty()
                            response_text = ""
                            for response in generate_response(retrieved_data):
                                response_text = response
                                response_placeholder.markdown(response_text)
                            st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        st.info("No relevant documents found.")
        else:
            st.warning("No indices available. Please create an index first.")

if __name__ == "__main__":
    main_pdf_chat()
