import os
import streamlit as st
import torch
from dotenv import load_dotenv
from model_provider import GraniteHF
from memory_storage import MemoryStore
from prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FinAssist Chatbot",
    page_icon="💰",
    layout="wide"
)

# Main title
st.title("💰 FinAssist - Your Personal Finance Assistant")
st.markdown("Ask me anything about finance, budgeting, or investment basics!")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Profile and persona settings
    profile_id = st.text_input("Profile ID", value="default", help="Unique identifier for your chat session")
    persona = st.selectbox(
        "Persona", 
        ["Student", "Professional", "Beginner", "Advanced"],
        help="Choose your financial knowledge level"
    )
    
    st.divider()
    
    # Model settings
    st.subheader("🤖 Model Configuration")
    model_id = st.text_input(
        "Model ID", 
        value="ibm-granite/granite-3.2-8b-instruct",
        help="HuggingFace model to use"
    )
    
    # Get HuggingFace token from environment or user input
    default_token = os.getenv("HUGGINGFACE_TOKEN", "")
    hf_token = st.text_input(
        "HuggingFace Token", 
        type="password", 
        value=default_token,
        help="Your HuggingFace API token"
    )
    
    st.divider()
    
    # Memory management
    st.subheader("🧠 Memory Management")
    if st.button("Clear Memory"):
        if "memory" in st.session_state:
            st.session_state.memory.clear()
            st.success("Memory cleared!")
    
    if st.button("Show Memory"):
        if "memory" in st.session_state:
            memory_data = st.session_state.memory.get_all()
            if memory_data:
                st.json(memory_data)
            else:
                st.info("No memories stored yet.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = MemoryStore(profile_id)

# Initialize model state
if 'model_ready' not in st.session_state:
    st.session_state.model_ready = False
    st.session_state.model_loading = False
    st.session_state.model = None

# Function to load model in background
def load_model():
    try:
        st.session_state.model_loading = True
        st.session_state.model = GraniteHF(
            model_id=model_id,
            hf_token=hf_token,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        st.session_state.model_ready = True
        st.sidebar.success("✅ Model loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize model: {str(e)}")
        st.sidebar.error("❌ Failed to load model. Please check your token and try again.")
    finally:
        st.session_state.model_loading = False

# Model loading UI
if hf_token:
    if not st.session_state.model_ready and not st.session_state.model_loading:
        if st.sidebar.button("🚀 Load Model"):
            load_model()
    elif st.session_state.model_loading:
        st.sidebar.info("⏳ Loading model... This may take a few minutes.")
    
    # Add a button to unload the model
    if st.session_state.model_ready:
        if st.sidebar.button("🔴 Unload Model"):
            if 'model' in st.session_state and st.session_state.model is not None:
                del st.session_state.model
            st.session_state.model_ready = False
            st.rerun()
else:
    st.warning("⚠️ Please provide a valid HuggingFace token in the sidebar to load the model.")

# Set model_ready for the rest of the app
model_ready = st.session_state.model_ready
if model_ready:
    granite = st.session_state.model

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about finance or budgeting..."):
    if not model_ready:
        st.warning("⚠️ Please load the model first using the sidebar button.")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Handle special commands
    if prompt.startswith("/remember "):
        key_value = prompt.replace("/remember ", "").split("=")
        if len(key_value) == 2:
            st.session_state.memory.set(key_value[0].strip(), key_value[1].strip())
            st.success(f"✅ Remembered: {key_value[0].strip()} = {key_value[1].strip()}")
        else:
            st.error("❌ Use format: /remember key=value")
    elif prompt.strip().lower() == "/clear":
        st.session_state.memory.clear()
        st.success("🧹 Memory cleared!")
    elif prompt.strip().lower() == "what do you remember?":
        memory_data = st.session_state.memory.get_all()
        if memory_data:
            st.info("🧠 Here's what I remember:")
            st.json(memory_data)
        else:
            st.info("🧠 I don't have any memories stored yet.")
    else:
        # Regular chat response
        if not model_ready:
            st.error("❌ Model not ready. Please check your HuggingFace token.")
        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner('🤔 Thinking...'):
                        # Prepare context with persona and memory
                        context = f"""{SYSTEM_PROMPT}
                        
                        User Profile:
                        - Persona: {persona}
                        - Memory Context: {st.session_state.memory.get_all()}
                        
                        Please provide a helpful and accurate response to the user's query."""
                        
                        # Get response from model with generation parameters
                        response = granite.chat(
                            system_prompt=context,
                            user_message=prompt,
                            max_new_tokens=1024,
                            temperature=0.7,
                            top_p=0.9,
                            repetition_penalty=1.1
                        )
                        
                        # Check for error in response
                        if any(keyword in response.lower() for keyword in ["error", "apologize", "sorry"]):
                            st.error("I encountered an issue generating a response. " + 
                                    "Please try again or rephrase your question.")
                        else:
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
            except Exception as e:
                error_msg = f"❌ An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Add helpful information at the bottom
with st.expander("💡 How to use this chatbot"):
    st.markdown("""
    **Special Commands:**
    - `/remember key=value` - Store information for future reference
    - `/clear` - Clear all stored memories
    - `what do you remember?` - Show all stored memories
    
    **Example Questions:**
    - "How do I create a budget?"
    - "What are the basics of investing?"
    - "How can I save money as a student?"
    - "What's the difference between stocks and bonds?"
    """)

# Footer
st.markdown("---")
st.markdown("*Powered by Granite AI and Streamlit*")
