# Retrieval-Augmented Generation (RAG) App

## Overview
The RAG application is a Streamlit-based tool designed to generate detailed, context-aware responses to user queries. It leverages an AI language model (Qwen 2.5B) and incorporates optional web search capabilities through DuckDuckGo, providing retrieval-augmented generation. The app can be used to answer general questions with additional context gathered from live web searches.

## Features
- **AI-Powered Responses**: The application uses the Qwen 2.5B model to generate comprehensive answers to user questions.
- **Web Search Integration**: Includes the ability to perform web searches using DuckDuckGo's DDGS to provide additional context for the AI's response.
- **Interactive UI**: Built using Streamlit, with an intuitive layout that includes tabs for displaying responses, sources, related queries, metadata, and debug information.
- **Related Queries**: Automatically generates follow-up questions related to the provided response, encouraging deeper exploration of the topic.

## Installation
To run this app locally, you need Python 3.7+ and the required dependencies. Follow these steps to install and run the app:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

   The required dependencies include:
   - `streamlit`
   - `ollama`
   - `duckduckgo-search`

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage
1. **Enter a Query**: Type your question in the input box.
2. **Web Search Context**: Check the box if you want to include additional web search context for your question.
3. **Generate Response**: Click the "Generate Response" button to receive an AI-generated answer.

The app will display the AI response along with relevant sources, related queries, metadata, and debug information in separate tabs.

## Code Structure
- **`perform_duckduckgo_search(query, result_count)`**: This function performs a web search using DuckDuckGo's DDGS API to provide relevant context for the query.
- **`generate_rag_response(query, use_web_search)`**: Generates a response using the Ollama client, incorporating search results if requested.
- **`display_response(rag_response, sources, raw_search_results, related_queries)`**: Displays the AI-generated response along with relevant sources, related queries, and metadata in the Streamlit app.

## Tabs
The app organizes information into five tabs:
1. **AI Response**: Displays the generated response.
2. **Sources**: Lists the web sources used for context, including links and snippets.
3. **Related Queries**: Displays follow-up questions based on the response for further exploration.
4. **Metadata**: Shows details like the model used, response time, and processing duration.
5. **Debug Sources**: Displays raw search results used during response generation.

## Customization
- **Ollama Client Configuration**: Update the `Client` initialization to match your environment, including the host and headers.
- **Web Search Parameters**: The function `perform_duckduckgo_search()` can be adjusted to modify the number of search results and other parameters.

## Contributing
Feel free to fork this repository and submit pull requests if you have improvements to suggest. You can also open issues for bug reports or feature requests.

## License
This project is licensed under the MIT License.

## Credits
- **Streamlit** for the interactive UI.
- **Ollama** for the language model API.
- **DuckDuckGo** for web search functionality.

---

Made with ❤️ using [Streamlit](https://streamlit.io), [LangChain](https://langchain.com), and [Ollama](https://ollama.ai).


