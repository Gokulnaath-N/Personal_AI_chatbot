import streamlit as st
import tempfile
import os
import io
import wave
import numpy as np
from typing import Optional, Tuple
import base64

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from gtts import gTTS
    from io import BytesIO
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class SpeechRecognition:
    def __init__(self):
        """Initialize speech recognition capabilities"""
        self.recognizer = None
        self.microphone = None
        
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception as e:
                st.warning(f"Speech recognition initialization failed: {str(e)}")
    
    def transcribe_audio_file(self, audio_file) -> Optional[str]:
        """
        Transcribe audio file to text using Google Speech Recognition
        
        Args:
            audio_file: Audio file object from Streamlit
            
        Returns:
            Transcribed text or None if error
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            st.error("Speech recognition not available. Please install speech_recognition library.")
            return None
        
        try:
            # Convert Streamlit audio to WAV format
            audio_data = audio_file.read()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            # Use speech recognition
            with sr.AudioFile(tmp_path) as source:
                audio = self.recognizer.record(source)
                
            # Clean up
            os.unlink(tmp_path)
            
            # Transcribe using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.UnknownValueError:
            st.error("Could not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results from speech recognition service: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def transcribe_microphone(self) -> Optional[str]:
        """
        Transcribe audio from microphone in real-time
        
        Returns:
            Transcribed text or None if error
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            st.error("Speech recognition not available. Please install speech_recognition library.")
            return None
        
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Speak now!")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("Could not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results from speech recognition service: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error transcribing audio: {str(e)}")
            return None

class TextToSpeech:
    def __init__(self):
        """Initialize text-to-speech capabilities"""
        self.available = TTS_AVAILABLE
    
    def generate_speech(self, text: str, language: str = 'en', slow: bool = False) -> Optional[bytes]:
        """
        Generate speech from text using Google Text-to-Speech
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en', 'es', 'fr')
            slow: Whether to speak slowly
            
        Returns:
            Audio data as bytes or None if error
        """
        if not self.available:
            st.warning("Text-to-speech not available. Please install gtts library.")
            return None
        
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to bytes buffer
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            st.error(f"Error generating speech: {str(e)}")
            return None
    
    def get_available_languages(self) -> dict:
        """Get available languages for TTS"""
        return {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'hi': 'Hindi',
            'ar': 'Arabic'
        }

def create_audio_recorder():
    """
    Create an audio recorder widget for Streamlit
    
    Returns:
        Audio data if recorded, None otherwise
    """
    try:
        audio_bytes = st.audio_recorder(
            text="🎤 Click to record your question",
            recording_color="#e74c3c",
            neutral_color="#6c757d",
            icon_name="microphone",
            icon_size="2x"
        )
        return audio_bytes
    except Exception as e:
        st.error(f"Error creating audio recorder: {str(e)}")
        return None

def display_audio_player(audio_data: bytes, text: str = "Generated Audio"):
    """
    Display an audio player widget
    
    Args:
        audio_data: Audio data as bytes
        text: Label for the audio player
    """
    try:
        st.audio(audio_data, format="audio/mp3")
    except Exception as e:
        st.error(f"Error displaying audio: {str(e)}")

def create_speech_interface():
    """
    Create a comprehensive speech interface with recording and playback
    """
    st.markdown("### 🎤 Voice Input & Output")
    
    # Speech Recognition
    speech_rec = SpeechRecognition()
    
    # Audio Recording
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎙️ Record Your Question**")
        audio_bytes = create_audio_recorder()
        
        if audio_bytes:
            with st.spinner("🎵 Transcribing audio..."):
                transcribed_text = speech_rec.transcribe_audio_file(audio_bytes)
                if transcribed_text:
                    st.success(f"🎵 Transcribed: {transcribed_text}")
                    return transcribed_text
                else:
                    st.error("❌ Could not transcribe audio. Please try again.")
    
    with col2:
        st.markdown("**🔊 Text-to-Speech**")
        tts = TextToSpeech()
        
        if tts.available:
            tts_text = st.text_area("Enter text to convert to speech:", height=100)
            language = st.selectbox("Language:", list(tts.get_available_languages().keys()), format_func=lambda x: tts.get_available_languages()[x])
            slow_speech = st.checkbox("Slow speech")
            
            if st.button("🔊 Generate Speech") and tts_text:
                with st.spinner("Generating speech..."):
                    audio_data = tts.generate_speech(tts_text, language, slow_speech)
                    if audio_data:
                        st.success("✅ Speech generated!")
                        display_audio_player(audio_data, "Generated Speech")
        else:
            st.info("💡 Install gtts library for text-to-speech: `pip install gtts`")
    
    return None

# Global instances
speech_recognition = SpeechRecognition()
text_to_speech = TextToSpeech()
