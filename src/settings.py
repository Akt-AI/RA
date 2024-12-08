import streamlit as st
import os

# Default configuration
DEFAULT_CONFIG = {
    "llm_model": "openai-gpt-4",
    "embedding_model": "sentence-transformers/all-mpnet-base-v2",
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 0.9,
    "server_type": "TGI",  # Options: ollama, llamacpp, vLLM, TGI
    "server_endpoint": "http://localhost:8080",
    "api_token": "your-api-token",
    "vector_store_path": "./vectorstore",
    "retrieval_top_k": 10,
}

CONFIG_FILE = "./config.py"


def save_config(config):
    """Saves the configuration to a Python file."""
    with open(CONFIG_FILE, "w") as f:
        f.write("# Configuration for the RAG system\n\n")
        for key, value in config.items():
            if isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f"{key} = {value}\n")
    st.success(f"Configuration saved to {CONFIG_FILE}")


def load_config():
    """Loads the configuration from the Python file if it exists."""
    if os.path.exists(CONFIG_FILE):
        config = {}
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if line.strip() and not line.strip().startswith("#"):
                    key, value = line.strip().split(" = ", 1)
                    value = value.strip('"') if value.startswith('"') else eval(value)
                    config[key] = value
        return config
    return DEFAULT_CONFIG


def main_settings():
    st.title("🔧 RAG Config File Editor")
    st.markdown(
        """
        Configure your Retrieval-Augmented Generation (RAG) system easily with this tool.
        Once configured, the settings will be saved to a `config.py` file.
        """
    )

    # Load existing config or use default
    config = load_config()

    # LLM Configuration
    st.subheader("LLM Configuration")
    config["llm_model"] = st.text_input(
        "LLM Model (e.g., openai-gpt-4, llama-2-13b):", config["llm_model"]
    )
    config["embedding_model"] = st.text_input(
        "Embedding Model (e.g., sentence-transformers/all-mpnet-base-v2):", config["embedding_model"]
    )

    # Hyperparameters
    st.subheader("Hyperparameters")
    config["temperature"] = st.slider(
        "Temperature (0.0 - 1.0):", 0.0, 1.0, float(config["temperature"]), step=0.01
    )
    config["max_tokens"] = st.number_input(
        "Max Tokens:", min_value=1, max_value=4096, value=int(config["max_tokens"])
    )
    config["top_p"] = st.slider(
        "Top-p (Nucleus Sampling):", 0.0, 1.0, float(config["top_p"]), step=0.01
    )
    config["retrieval_top_k"] = st.number_input(
        "Retrieval Top-K:", min_value=1, max_value=100, value=int(config["retrieval_top_k"])
    )

    # Inference Server Configuration
    st.subheader("Inference Server")
    config["server_type"] = st.selectbox(
        "Inference Server Type:", ["ollama", "llamacpp", "vLLM", "TGI"], index=["ollama", "llamacpp", "vLLM", "TGI"].index(config["server_type"])
    )
    config["server_endpoint"] = st.text_input(
        "Server Endpoint (URL):", config["server_endpoint"]
    )
    config["api_token"] = st.text_input("API Token:", config["api_token"], type="password")

    # Vector Store Configuration
    st.subheader("Vector Store")
    config["vector_store_path"] = st.text_input(
        "Vector Store Path:", config["vector_store_path"]
    )

    # Save Config Button
    if st.button("Save Configuration"):
        save_config(config)

    # Display Current Config
    st.subheader("Current Configuration")
    st.code(config, language="python")


if __name__ == "__main__":
    main_settings()

