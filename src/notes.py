import os
import streamlit as st

# Directory to store notes
NOTES_DIR = "./markdown_notes"

# Ensure the notes directory exists
os.makedirs(NOTES_DIR, exist_ok=True)

def list_notes():
    """Lists all notes in the notes directory."""
    return [f.replace('.md', '') for f in os.listdir(NOTES_DIR) if f.endswith('.md')]

def read_note(note_name):
    """Reads the content of a note."""
    note_path = os.path.join(NOTES_DIR, f"{note_name}.md")
    with open(note_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_note(note_name, content):
    """Saves content to a Markdown note."""
    note_path = os.path.join(NOTES_DIR, f"{note_name}.md")
    with open(note_path, 'w', encoding='utf-8') as file:
        file.write(content)

def delete_note(note_name):
    """Deletes a Markdown note."""
    note_path = os.path.join(NOTES_DIR, f"{note_name}.md")
    if os.path.exists(note_path):
        os.remove(note_path)

def main_notes():
    st.title("📝 Markdown Notes Taking Tool")
    st.markdown(
        """
        ### Features:
        - Create new notes using Markdown.
        - Edit and save existing notes.
        - Delete notes you no longer need.
        - Render notes in Markdown for better readability.
        """
    )

    # Use session state to handle note selection and content
    if "selected_note" not in st.session_state:
        st.session_state.selected_note = "Create New Note"
    if "note_content" not in st.session_state:
        st.session_state.note_content = ""

    # Sidebar for managing notes
    st.sidebar.title("Notes Manager")
    notes = list_notes()
    st.session_state.selected_note = st.sidebar.selectbox("Select a note:", ["Create New Note"] + notes)

    # If creating a new note
    if st.session_state.selected_note == "Create New Note":
        st.subheader("Create a New Note")
        note_name = st.text_input("Note Title (no special characters):", placeholder="Enter note title here")
        st.session_state.note_content = st.text_area("Note Content (Markdown Supported):", height=300, placeholder="Write your note here in Markdown...")

        # Save the new note
        if st.button("Save Note"):
            if note_name.strip():
                save_note(note_name.strip(), st.session_state.note_content)
                st.success(f"Note '{note_name}' saved successfully!")
                st.session_state.selected_note = note_name.strip()  # Automatically select the newly created note
            else:
                st.warning("Please provide a title for your note.")
    else:
        # If editing an existing note
        st.subheader(f"Editing Note: {st.session_state.selected_note}")
        st.session_state.note_content = st.text_area(
            "Note Content (Markdown Supported):",
            value=read_note(st.session_state.selected_note),
            height=300
        )

        # Save changes to the note
        if st.button("Save Changes"):
            save_note(st.session_state.selected_note, st.session_state.note_content)
            st.success(f"Changes to '{st.session_state.selected_note}' saved successfully!")

        # Render the Markdown
        st.markdown("---")
        st.subheader("Rendered Note (Markdown)")
        st.markdown(st.session_state.note_content, unsafe_allow_html=True)

        # Delete the note
        if st.button("Delete Note"):
            delete_note(st.session_state.selected_note)
            st.warning(f"Note '{st.session_state.selected_note}' deleted successfully!")
            st.session_state.selected_note = "Create New Note"  # Reset to creating a new note
            st.session_state.note_content = ""  # Clear the content area

if __name__ == "__main__":
    main_notes()
