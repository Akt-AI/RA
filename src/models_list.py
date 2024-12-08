import streamlit as st
import requests

# Function to fetch models from Ollama server
def fetch_ollama_models(base_url):
    try:
        response = requests.get(f"{base_url}/api/tags")
        response.raise_for_status()
        models_data = response.json().get("models", [])
        return models_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching models from Ollama: {e}")
        return []

def main_models_list():
    st.title("🌟 Fancy Ollama Model Explorer 🌟")
    st.markdown(
        """
        Explore the available models hosted on your Ollama server with detailed information and a stylish interface.
        """
    )

    # Base URL for Ollama server
    ollama_base_url = st.text_input("Enter Ollama Server Base URL:", value="http://localhost:11434")

    if st.button("Fetch Models"):
        if ollama_base_url:
            with st.spinner("Fetching models from Ollama..."):
                # st.components.v1.iframe(url, height=600, scrolling=True)
                models = fetch_ollama_models(ollama_base_url)
                if models:
                    st.subheader("✨ Available Models ✨")
                    for model in models:
                        # Fancy card for each model
                        st.markdown(
                            f"""
                            <div style="background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; border: 1px solid #ddd; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
                                <h3 style="color: #007bff; font-family: Arial, sans-serif;">{model.get('name', 'Unknown')}</h3>
                                <p><strong>Modified At:</strong> {model.get('modified_at', 'Unknown')}</p>
                                <p><strong>Size:</strong> {model.get('size', 'Unknown')} bytes</p>
                                <p><strong>Parameter Size:</strong> {model['details'].get('parameter_size', 'Unknown')}</p>
                                <p><strong>Quantization Level:</strong> {model['details'].get('quantization_level', 'Unknown')}</p>
                                <p><strong>Format:</strong> {model['details'].get('format', 'Unknown')}</p>
                                <p><strong>Digest:</strong> {model.get('digest', 'Unknown')}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.warning("No models found on the Ollama server.")
        else:
            st.error("Please enter a valid Ollama server base URL.")
    
    url = "https://ollama.com/search"
    hf = "https://huggingface.co/models"
    st.markdown("[Ollama Models](https://ollama.com/search)", unsafe_allow_html=True)
    st.markdown("[Hugging Face Models](https://huggingface.co/models)", unsafe_allow_html=True)


if __name__ == "__main__":
    main_models_list()
