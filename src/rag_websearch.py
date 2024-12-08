import streamlit as st
from ollama import Client
from duckduckgo_search import DDGS
import json
import os
import requests

# Default file paths
INDEX_DIR = "indices"
os.makedirs(INDEX_DIR, exist_ok=True)
OLLAMA_API_URL = "http://localhost:11434"
# EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_MODEL = "mxbai-embed-large:latest"

GENERATION_MODEL = "qwen2.5:0.5b"

# Function to perform DuckDuckGo search
def perform_duckduckgo_search(query, result_count=10):
    """Perform a web search using DuckDuckGo's DDGS."""
    results = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=result_count):
                results.append({
                    "title": result.get("title", "No Title"),
                    "link": result.get("href", "No Link"),
                    "snippet": result.get("body", "No Snippet")
                })
    except Exception as e:
        st.error(f"Error in DuckDuckGo search: {e}")
    return results

# Function to generate response with optional web search
def generate_rag_response(query, use_web_search=False):
    search_results = perform_duckduckgo_search(query, result_count=10) if use_web_search else []
    
    # Construct prompt
    prompt = f"User Query: {query}\n\n"
    if search_results:
        prompt += "Web Search Results:\n"
        for result in search_results:
            prompt += f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}\n\n"
    prompt += "Based on the above information, provide a detailed and comprehensive answer."
    
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

# Function to display AI response in Streamlit
def display_response(response_text, sources, raw_search_results, related_queries):
    st.success("✅ Response successfully generated!")
    
    # Tabs for organized display
    tabs = st.tabs(["🧠 AI Response", "🔗 Sources", "❓ Related Queries", "📊 Metadata", "🐞 Debug"])
    
    with tabs[0]:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_text = ""
            for response in generate_rag_response(response_text):
                response_text = response
                response_placeholder.markdown(response_text)

            # st.markdown("### 🧠 AI-Generated Response")
            # st.markdown(
            #     f"""
            #     <div style="background-color:#f9f9f9; padding:15px; border-radius:10px; border:1px solid #ddd;">
            #     {response_text}
            #     </div>
            #     """, unsafe_allow_html=True
            # )
        
    with tabs[1]:
        st.markdown("### 🔗 Sources")
        if sources:
            for source in sources:
                url = source.split("](")[1].split(")")[0]
                print(url)
                if "youtube.com" in url:
                    st.video(url)
                st.markdown(source, unsafe_allow_html=True)
        else:
            st.write("No sources were used for this response.")
    
    with tabs[2]:
        st.markdown("### ❓ Related Queries")
        for query in related_queries:
            if st.button(f"🔍 {query}"):
                st.session_state["query_input"] = query
                st.experimental_rerun()
    
    with tabs[3]:
        st.markdown("### 📊 Metadata")
        st.write("No additional metadata available.")
    
    with tabs[4]:
        st.markdown("### 🐞 Debug Information")
        st.write("Raw search results:")
        for result in raw_search_results:
            st.write(result)

# Main application function
def main_websearch():
    st.title("🤖 RAG with Web Search")
    st.markdown(
        """
        Welcome! Enter your question below to receive an AI-generated response.
        Enable web search to fetch additional context from the web.
        """
    )
    
    query = st.text_input("🔍 Ask your question:", placeholder="Type something like 'Why is the sky blue?'", key="query_input")
    use_web_search = st.checkbox("🔗 Use Web Search for Additional Context")
    
    if st.button("Generate Response"):
        if query.strip():
            with st.spinner("💡 Generating your response... Please wait."):
                try:
                    response_generator = generate_rag_response(query, use_web_search)
                    response_text = next(response_generator, "")
                    sources = [f"- [{r['title']}]({r['link']})\n  Snippet: {r['snippet']}" for r in perform_duckduckgo_search(query, 10)]
                    related_queries = [
                        f"Can you explain '{query}' in more detail?",
                        f"What are the implications of '{query}'?",
                        f"How does the information about '{query}' apply to daily life?"
                    ]
                    display_response(response_text, sources, sources, related_queries)
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")
        else:
            st.warning("⚠️ Please enter a valid query.")
    
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit, LangChain, and Ollama.")

# Run the app
if __name__ == "__main__":
    main_websearch()
