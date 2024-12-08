import streamlit as st
import ollama
import subprocess
import shutil
from pathlib import Path
import os
import pickle
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Default file paths
INDEX_DIR = "indices"
os.makedirs(INDEX_DIR, exist_ok=True)

# Helper function to get a list of available indices
def get_indices():
    return [f.split(".")[0] for f in os.listdir(INDEX_DIR) if f.endswith(".pkl")]

# Step 1: Clone the GitHub Repository
def clone_repo(repo_url, clone_dir):
    try:
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
        return f"Repository cloned to {clone_dir}"
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to clone repository: {e}")
        raise

# Step 2: Crawl a URL Recursively
def crawl_url(base_url, depth=2):
    visited = set()
    urls = [base_url]
    for _ in range(depth):
        new_urls = []
        for url in urls:
            if url not in visited:
                visited.add(url)
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    for link in soup.find_all("a", href=True):
                        absolute_url = urljoin(base_url, link["href"])
                        if base_url in absolute_url and absolute_url not in visited:
                            new_urls.append(absolute_url)
                except requests.RequestException as e:
                    st.warning(f"Failed to crawl {url}: {e}")
        urls = new_urls
    return visited

# Step 3: Load Text Files from Directory or URLs
def load_text_data(source, is_url=False):
    """
    Load text data from a directory or URLs.

    Parameters:
        source (str or list): Directory path or list of URLs.
        is_url (bool): If True, treat the source as URLs.

    Returns:
        dict: A dictionary where keys are file paths or URLs and values are the text content.
    """
    data = {}
    if is_url:
        st.info("Loading content from URLs...")
        for url in source:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text()
                data[url] = text
            except requests.RequestException as e:
                st.warning(f"Failed to load content from {url}: {e}")
    else:
        for file_path in Path(source).rglob("*.*"):
            if file_path.suffix in [".py", ".md", ".txt", ".js", ".java", ".c", ".cpp"]:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        data[str(file_path)] = f.read()
                except Exception as e:
                    st.warning(f"Failed to read file {file_path}: {e}")
    return data

# Step 4: Index Data
def index_data(data, index_name):
    collection = {"embeddings": [], "documents": [], "metadata": []}
    st.info("Generating embeddings...")
    for path, content in data.items():
        try:
            response = ollama.embeddings(model="mxbai-embed-large", prompt=content)
            embedding = response["embedding"]
            collection["embeddings"].append(embedding)
            collection["documents"].append(content)
            collection["metadata"].append({"path": path})
        except Exception as e:
            st.error(f"Error generating embeddings for {path}: {e}")
    with open(os.path.join(INDEX_DIR, f"{index_name}.pkl"), "wb") as f:
        pickle.dump(collection, f)
    st.success(f"Index '{index_name}' saved.")
    return collection

# Load an Existing Index
def load_index(index_name):
    try:
        with open(os.path.join(INDEX_DIR, f"{index_name}.pkl"), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error(f"Index '{index_name}' not found.")
        raise

# Step 5: Query the Index
def query_index(prompt, collection):
    try:
        # Generate embedding for the query
        response = ollama.embeddings(model="mxbai-embed-large", prompt=prompt)
        query_embedding = response["embedding"]

        # Validate embedding shapes
        valid_embeddings = []
        valid_documents = []
        valid_metadata = []
        for i, embedding in enumerate(collection["embeddings"]):
            if len(embedding) == len(query_embedding):
                valid_embeddings.append(embedding)
                valid_documents.append(collection["documents"][i])
                valid_metadata.append(collection["metadata"][i])

        # Handle case where no valid embeddings exist
        if not valid_embeddings:
            st.error("No valid embeddings found in the index.")
            return None, None

        # Compute cosine similarity
        similarities = [
            np.dot(query_embedding, e) / (np.linalg.norm(query_embedding) * np.linalg.norm(e))
            for e in valid_embeddings
        ]
        max_index = np.argmax(similarities)
        return valid_documents[max_index], valid_metadata[max_index]["path"]
    except Exception as e:
        st.error(f"Error querying index: {e}")
        raise

# Step 6: Generate a Streaming Response
def generate_response_stream(data, prompt):
    full_prompt = f"Using this data: {data}. Respond to this prompt: {prompt}"
    for response_chunk in ollama.generate(model="qwen2.5:0.5b", prompt=full_prompt, stream=True):
        try:
            if "response" in response_chunk:
                yield response_chunk["response"]
            else:
                st.warning("No 'response' key in response chunk.")
        except KeyError as e:
            st.error(f"Error processing response chunk: {e}")

# Streamlit App
def main_rag_git():
    st.title("🔍 RAG with Github & Web Chat")
    st.sidebar.header("Options")

    if "indices" not in st.session_state:
        st.session_state.indices = get_indices()

    # User inputs
    mode = st.sidebar.radio("Mode", ["GitHub Repository", "Web URL"])
    index_name = st.sidebar.text_input("Index Name", value="default_index")
    depth = st.sidebar.slider("Crawl Depth (for URLs)", 1, 5, 2)
    allow_new_index = st.sidebar.checkbox("Allow New Index Creation", value=True)

    if mode == "GitHub Repository":
        repo_url = st.text_input("Enter GitHub Repository URL:")
        clone_dir = "cloned_repo"
        if st.button("Process GitHub Repository"):
            if allow_new_index or index_name not in st.session_state.indices:
                st.info("Cloning repository...")
                clone_repo(repo_url, clone_dir)
                st.info("Loading repository files...")
                repo_files = load_text_data(clone_dir)
                st.info("Indexing repository...")
                index_data(repo_files, index_name)
                shutil.rmtree(clone_dir)
                st.session_state.indices = get_indices()
            else:
                st.info(f"Index '{index_name}' already exists. Skipping indexing.")

    elif mode == "Web URL":
        base_url = st.text_input("Enter Base URL to Crawl:")
        if st.button("Crawl and Index"):
            if allow_new_index or index_name not in st.session_state.indices:
                st.info("Crawling URLs...")
                urls = crawl_url(base_url, depth)
                st.info("Loading content from crawled URLs...")
                url_data = load_text_data(urls, is_url=True)
                st.info("Indexing content...")
                index_data(url_data, index_name)
                st.session_state.indices = get_indices()
            else:
                st.info(f"Index '{index_name}' already exists. Skipping indexing.")

    # Query section
    st.header("Query the Index")
    if st.session_state.indices:
        selected_index = st.selectbox("Select an Index", st.session_state.indices)
        user_query = st.text_input("Enter your query:")
        if st.button("Query"):
            collection = load_index(selected_index)
            retrieved_data, file_path = query_index(user_query, collection)
            st.write(f"Retrieved from: `{file_path}`")
            st.write("### Response (Streaming):")
            response_placeholder = st.empty()
            response_text = ""
            for chunk in generate_response_stream(retrieved_data, user_query):
                response_text += chunk
                response_placeholder.write(response_text)
    else:
        st.warning("No indices found. Please create one first.")

if __name__ == "__main__":
    main_rag_git()
