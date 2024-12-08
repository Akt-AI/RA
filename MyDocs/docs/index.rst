AI Chat Assistant
=================

Welcome to the **AI Chat Assistant** documentation. This application is a feature-rich, AI-powered chat platform designed for intuitive and seamless interactions.

Overview
--------

The AI Chat Assistant allows users to:

- Engage in conversations with an intelligent AI chat assistant.
- Customize creativity levels using the model temperature slider.
- Save and load chat histories for future reference.
- Securely register and log in for a personalized experience.
- Explore interactive tools like image generation based on prompts.

Features
--------

1. **AI-Powered Chat**:
   - Provides meaningful and context-aware responses using advanced AI models.

2. **Customizable Creativity**:
   - Adjust the creativity level of responses by modifying the model temperature slider.

3. **Chat Management**:
   - Save ongoing conversations to revisit later.
   - Load previously saved chat histories seamlessly.

4. **User Authentication**:
   - Securely register and log in to access personalized features.

5. **Dynamic Interaction**:
   - Generate images based on textual prompts.

6. **Easy Navigation**:
   - A simple and intuitive interface for smooth user experience.

Setup and Installation
-----------------------

### Prerequisites

Ensure you have the following installed:

- Python 3.7 or higher
- Required Python libraries (Streamlit, SQLite3, Requests, etc.)

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/ai-chat-assistant.git
   cd ai-chat-assistant
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   streamlit run app.py
   ```

4. Access the application in your web browser at:

   ```
   http://localhost:8501
   ```

User Guide
----------

### Landing Page

- **Introduction and Features**:
  - The landing page provides an overview of the app’s features and capabilities.
- **Login and Register Buttons**:
  - Quickly navigate to login or register for a new account.

### Authentication

- **Login**:
  - Enter your registered username and password to access the app.
- **Register**:
  - Create a new account by entering a unique username and password.

### Chat Interface

- **Start a Conversation**:
  - Type your message in the input box and receive AI-generated responses.
- **Adjust Creativity**:
  - Use the temperature slider to control the response creativity.

### Chat Management

- **Save Chat History**:
  - Automatically save your conversations for future reference.
- **Load Previous Chats**:
  - Access saved chats from the sidebar.

### Image Generation

- **Generate Images**:
  - Use the `/gen` command followed by a prompt to create images dynamically.

Technical Details
------------------

### Configuration

- **Database**:
  - Uses SQLite for storing user authentication details.
- **API Integration**:
  - Communicates with the AI model server via REST API calls.

### File Structure

```
|-- app.py               # Main application file
|-- user_data.db         # SQLite database for user data
|-- chat_history/        # Directory for saved chat histories
|-- requirements.txt     # Python dependencies
```

### Customization

- Modify the **OLLAMA_API_URL** in `app.py` to point to your AI model server.
- Adjust the **EMOJI_LIST** or other constants for a personalized touch.

Support
-------

For issues or feature requests, please contact the developer team or raise an issue on the [GitHub repository](https://github.com/your-repo/ai-chat-assistant/issues).

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.

Enjoy using the AI Chat Assistant to enhance your productivity and engagement!


