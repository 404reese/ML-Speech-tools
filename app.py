import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
from tempfile import NamedTemporaryFile
from audio_recorder_streamlit import audio_recorder

# Initialize services
recognizer = sr.Recognizer()
translator = Translator()

# Set page configuration
st.set_page_config(
    page_title="Multilingual Speech Tool",
    page_icon="🔊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: black;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .result-box {
        background-color: #000;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("🔊 Multilingual Speech & Translation Tool")
st.subheader("Convert speech to text, text to speech, and translate between languages")

# Create tabs for different functions
tab1, tab2, tab3 = st.tabs(["Speech to Text", "Text to Speech", "Translation"])

# --------------------- Speech to Text Tab ---------------------
with tab1:
    st.header("🎤 Speech to Text Conversion")
    
    # Option to record audio or upload file
    recording_mode = st.radio("Choose input method:", 
                             ["Record Audio", "Upload Audio File"],
                             horizontal=True)
    
    if recording_mode == "Record Audio":
        audio_bytes = audio_recorder(
            text="Click to record",
            pause_threshold=3.0,
            sample_rate=44100
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            with NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                with sr.AudioFile(f.name) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        st.success(f"Recognized text: {text}")
                        st.session_state.text_output = text
                    except sr.UnknownValueError:
                        st.error("Could not understand audio")
                    except sr.RequestError as e:
                        st.error(f"Service error: {e}")
    
    else:
        uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3"])
        if uploaded_file:
            with NamedTemporaryFile(suffix=os.path.splitext(uploaded_file.name)[1]) as f:
                f.write(uploaded_file.getbuffer())
                with sr.AudioFile(f.name) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        st.success(f"Recognized text: {text}")
                        st.session_state.text_output = text
                    except sr.UnknownValueError:
                        st.error("Could not understand audio")
                    except sr.RequestError as e:
                        st.error(f"Service error: {e}")

# --------------------- Text to Speech Tab ---------------------
with tab2:
    st.header("📢 Text to Speech Conversion")
    
    input_text = st.text_area("Enter text to convert:", 
                            value=st.session_state.get('text_output', ''),
                            height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Select language:", 
                               ["English", "Hindi", "French", "Spanish", "Japanese"])
    with col2:
        speed = st.slider("Select speed:", 0.5, 2.0, 1.0, 0.1)
    
    if st.button("Generate Audio"):
        if input_text.strip():
            lang_code = {
                "English": "en",
                "Hindi": "hi",
                "French": "fr",
                "Spanish": "es",
                "Japanese": "ja"
            }[language]
            
            tts = gTTS(text=input_text, lang=lang_code, slow=(speed < 0.8))
            with NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tts.save(f.name)
                st.audio(f.name, format="audio/mp3")
                st.markdown(f"**{language} audio generated successfully!**")
                st.markdown(f"Download: [Right-click to save]({f.name})")
        else:
            st.warning("Please enter some text first")

# --------------------- Translation Tab ---------------------
with tab3:
    st.header("🌐 Text Translation")
    
    source_text = st.text_area("Enter text to translate:", 
                             value=st.session_state.get('text_output', ''),
                             height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        src_lang = st.selectbox("Source language:", 
                               ["English", "Hindi", "French", "Spanish", "Japanese"])
    with col2:
        dest_lang = st.selectbox("Target language:", 
                                ["Hindi", "English", "French", "Spanish", "Japanese"])
    
    if st.button("Translate"):
        if source_text.strip():
            try:
                translated = translator.translate(
                    source_text,
                    src=src_lang.lower(),
                    dest=dest_lang.lower()
                )
                st.success(f"Translated text ({dest_lang}):")
                st.markdown(f"<div class='result-box'>{translated.text}</div>", 
                           unsafe_allow_html=True)
                
                # Add option to convert translation to speech
                if st.button("Convert Translation to Speech"):
                    lang_code = dest_lang.lower()
                    tts = gTTS(text=translated.text, lang=lang_code)
                    with NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                        tts.save(f.name)
                        st.audio(f.name, format="audio/mp3")
            except Exception as e:
                st.error(f"Translation error: {str(e)}")
        else:
            st.warning("Please enter text to translate")

# Footer
st.markdown("---")
st.markdown("Developed by [Your Name]")