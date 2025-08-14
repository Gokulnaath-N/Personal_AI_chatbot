# FinAssist Chatbot

A Streamlit-based financial assistant chatbot powered by Granite AI that helps users with personal finance, budgeting, and investment basics.

## Features

- 💬 Interactive chat interface
- 🧠 Memory system to remember user preferences
- 🎯 Persona-based responses (Student, Professional, Beginner, Advanced)
- 💰 Financial education and guidance
- 🔒 Secure token management
- 📱 Responsive web interface

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get HuggingFace Token**
   - Go to [HuggingFace](https://huggingface.co/settings/tokens)
   - Create a new token
   - Copy the token

3. **Set Environment Variable (Optional)**
   Create a `.env` file in the project root:
   ```
   HUGGINGFACE_TOKEN=your_token_here
   ```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### Basic Chat
- Simply type your financial questions in the chat input
- The bot will respond based on your selected persona

### Special Commands
- `/remember key=value` - Store information for future reference
- `/clear` - Clear all stored memories
- `what do you remember?` - Show all stored memories

### Example Questions
- "How do I create a budget?"
- "What are the basics of investing?"
- "How can I save money as a student?"
- "What's the difference between stocks and bonds?"

## Configuration

In the sidebar, you can:
- Set your Profile ID for session management
- Choose your persona (Student, Professional, Beginner, Advanced)
- Configure the AI model
- Manage your HuggingFace token
- Clear or view stored memories

## Files Structure

- `app.py` - Main Streamlit application
- `model_provider.py` - AI model integration
- `memory_storage.py` - Memory management system
- `prompts.py` - System prompts and instructions
- `requirements.txt` - Python dependencies
- `memories.json` - Stored user memories (created automatically)

## Requirements

- Python 3.7+
- Streamlit
- HuggingFace Hub
- Python-dotenv

## Note

This chatbot is designed for educational purposes and provides general financial guidance. Always consult with qualified financial professionals for specific investment advice.
