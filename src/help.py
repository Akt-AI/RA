import os
import streamlit as st

def list_markdown_files(directory):
    """Lists all Markdown files in a given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.md')]

def read_markdown_file(filepath):
    """Reads the content of a Markdown file."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def save_markdown_file(filepath, content):
    """Saves updated Markdown content back to the file."""
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

def main_help():
    st.title("Editable Markdown Renderer")
    st.markdown(
        """
        ### Instructions:
        - Specify a directory containing Markdown files (`.md`).
        - Select a file from the dropdown to view its content.
        - Edit the content in the text area, and save your changes.
        - See the rendered Markdown update in real-time!
        """
    )
    
    # Specify the directory containing Markdown files
    markdown_dir = st.text_input("Enter the directory path:", value="./markdown_files")
    
    # Check if the directory exists
    if not os.path.exists(markdown_dir):
        st.error(f"The directory '{markdown_dir}' does not exist.")
        return
    
    # List all Markdown files in the directory
    markdown_files = list_markdown_files(markdown_dir)
    
    if not markdown_files:
        st.warning(f"No Markdown files found in '{markdown_dir}'.")
        return
    
    # Select a Markdown file
    selected_file = st.selectbox("Select a Markdown file:", markdown_files)
    
    if selected_file:
        filepath = os.path.join(markdown_dir, selected_file)
        
        # Read the content of the selected file
        markdown_content = read_markdown_file(filepath)
        
        # Editable text area for Markdown content
        updated_content = st.text_area(
            "Edit Markdown Content:",
            markdown_content,
            height=300
        )
        
        # Save button
        if st.button("Save Changes"):
            save_markdown_file(filepath, updated_content)
            st.success(f"Changes saved to '{selected_file}'!")
        
        # Render the Markdown
        st.markdown("---")
        st.subheader("Rendered Markdown")
        st.markdown(updated_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main_help()
