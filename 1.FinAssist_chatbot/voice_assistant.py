import streamlit as st
from speech_utils import SpeechRecognition, TextToSpeech, create_audio_recorder
from voice_commands import voice_commands
import time

def create_voice_assistant_page():
    """Create a comprehensive voice assistant page"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🎤 Voice Assistant</h1>
        <p>Hands-free financial management with voice commands</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize speech components
    speech_rec = SpeechRecognition()
    tts = TextToSpeech()
    
    # Voice Assistant Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎙️ Voice Recording")
        audio_bytes = create_audio_recorder()
        
        if audio_bytes:
            with st.spinner("🎵 Processing voice input..."):
                transcribed_text = speech_rec.transcribe_audio_file(audio_bytes)
                if transcribed_text:
                    st.success(f"🎵 Transcribed: {transcribed_text}")
                    
                    # Process voice command
                    voice_response = voice_commands.process_voice_command(transcribed_text)
                    if voice_response:
                        st.info("🎤 Voice Command Executed!")
                        st.markdown(voice_response)
                        
                        # Auto-generate speech for response
                        if tts.available:
                            with st.spinner("🔊 Generating speech response..."):
                                audio_data = tts.generate_speech(voice_response, 'en', False)
                                if audio_data:
                                    st.audio(audio_data, format="audio/mp3")
                    else:
                        st.info("💬 Regular conversation mode - this will be sent to the AI assistant")
                else:
                    st.error("❌ Could not transcribe audio. Please try again.")
    
    with col2:
        st.markdown("### 🔊 Text-to-Speech")
        if tts.available:
            tts_text = st.text_area("Enter text to convert to speech:", height=150)
            language = st.selectbox(
                "Language:", 
                list(tts.get_available_languages().keys()), 
                format_func=lambda x: tts.get_available_languages()[x]
            )
            slow_speech = st.checkbox("Slow speech")
            
            if st.button("🔊 Generate Speech") and tts_text:
                with st.spinner("Generating speech..."):
                    audio_data = tts.generate_speech(tts_text, language, slow_speech)
                    if audio_data:
                        st.success("✅ Speech generated!")
                        st.audio(audio_data, format="audio/mp3")
        else:
            st.info("💡 Install gtts library for text-to-speech: `pip install gtts`")
    
    with col3:
        st.markdown("### ⚙️ Voice Settings")
        st.markdown("**Voice Recognition:**")
        if speech_rec.recognizer:
            st.success("✅ Microphone ready")
        else:
            st.error("❌ Microphone not available")
        
        st.markdown("**Text-to-Speech:**")
        if tts.available:
            st.success("✅ TTS ready")
        else:
            st.warning("⚠️ TTS not available")
        
        # Voice command help
        if st.button("📖 Show Voice Commands"):
            st.markdown(voice_commands.show_help(""))
    
    # Voice Command Examples
    st.markdown("## 🎯 Quick Voice Commands")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Navigation Commands")
        st.markdown("""
        - **"Go to dashboard"** - Switch to main dashboard
        - **"Go to settings"** - Open configuration
        - **"Go to analytics"** - View financial analytics
        - **"Go to chat"** - Open AI chat assistant
        """)
        
        st.markdown("### Memory Commands")
        st.markdown("""
        - **"Remember [information]"** - Store information
        - **"What do you remember"** - Show stored memories
        - **"Clear"** - Clear chat history
        """)
    
    with col2:
        st.markdown("### Financial Help Commands")
        st.markdown("""
        - **"Budget help"** - Get budgeting advice
        - **"Investment help"** - Get investment guidance
        - **"Savings help"** - Get savings tips
        - **"Expenses help"** - Get expense management advice
        """)
        
        st.markdown("### Data Commands")
        st.markdown("""
        - **"Save"** - Save current data
        - **"Export"** - Export financial data
        - **"Help"** - Show all commands
        """)
    
    # Voice Assistant Status
    st.markdown("## 📊 Voice Assistant Status")
    
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    
    with status_col1:
        st.metric("Voice Recognition", "✅ Active" if speech_rec.recognizer else "❌ Inactive")
    
    with status_col2:
        st.metric("Text-to-Speech", "✅ Active" if tts.available else "❌ Inactive")
    
    with status_col3:
        st.metric("Voice Commands", "✅ Ready")
    
    with status_col4:
        st.metric("AI Integration", "✅ Connected")
    
    # Voice Tips
    st.markdown("## 💡 Voice Interaction Tips")
    
    tips = [
        "🎤 **Speak clearly** - Enunciate your words for better recognition",
        "🔇 **Reduce background noise** - Find a quiet environment",
        "📏 **Keep it concise** - Short commands work better",
        "🎯 **Use specific commands** - Try the examples above",
        "🔄 **Try again** - If recognition fails, try rephrasing",
        "📱 **Check microphone** - Ensure your device microphone is working"
    ]
    
    for tip in tips:
        st.markdown(tip)
    
    # Voice Assistant Demo
    st.markdown("## 🎬 Voice Assistant Demo")
    
    if st.button("🎤 Start Voice Demo"):
        st.info("🎤 Demo Mode: Try saying 'help' to see available commands")
        
        # Simulate voice command processing
        demo_commands = [
            "Go to dashboard",
            "Remember my monthly budget is $3000",
            "What do you remember",
            "Budget help",
            "Clear"
        ]
        
        for i, command in enumerate(demo_commands):
            time.sleep(1)
            with st.expander(f"Demo Command {i+1}: '{command}'"):
                response = voice_commands.process_voice_command(command)
                st.markdown(f"**Response:** {response}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🎤 Voice Assistant - Hands-free financial management</p>
    </div>
    """, unsafe_allow_html=True)
