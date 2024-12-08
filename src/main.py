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


# Main app with tabs
def main():
    st.set_page_config(page_title="Streamlit Tabs Example", layout="wide")
    chat, tab2, tab3, tab4, tab5, agents, workflows, help, notes, chat_history, settings, models_apis  \
               = st.tabs(["Chat", "🔍 Web Search RAG", "📂 GitHub & URL Chat", \
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
        main_chat()

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

    # with apis:
    #     pass

if __name__ == "__main__":
    main()
