import os
import streamlit as st
import yt_dlp
import whisper
from docx import Document
from collections import Counter
import re

# Set page configuration
st.set_page_config(page_title="YouTube Audio Transcriber", page_icon="🎤", layout="wide")

# Streamlit UI Styling
st.markdown("""
    <style>
        .stTextInput>div>div>input { font-size: 16px; }
        .stButton>button { width: 100%; font-size: 16px; border-radius: 10px; }
        .stMarkdown { font-size: 16px; }
        .stAlert { font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.title("🎙️ YouTube Audio Transcriber")
st.write("Download audio from a YouTube video and generate a transcript using Whisper.")

video_url = st.text_input("🔗 Enter YouTube Video URL", "")

def download_youtube_audio(url):
    output_dir = "temp_audio"
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)

    st.success(f"✅ Downloaded: {audio_path}")
    return audio_path

# Function to generate a Word file
def save_transcript_to_docx(transcript, filename="transcript.docx"):
    doc = Document()
    doc.add_heading("YouTube Video Transcript", level=1)
    doc.add_paragraph(transcript)
    doc_path = os.path.join("temp_audio", filename)
    doc.save(doc_path)
    return doc_path

# Function to translate transcript
def translate_text(text, target_language):
    translator = pipeline("translation_en_to_fr")  # Change model for different languages
    translated_text = translator(text, max_length=400)[0]["translation_text"]
    return translated_text

# Function to analyze word frequency
def get_word_frequency(text):
    words = re.findall(r'\b\w+\b', text.lower())  # Extract words
    word_counts = Counter(words)
    return word_counts.most_common(10)  # Return top 10 words

# Sidebar for additional functionalities
with st.sidebar:
    st.header("⚙️ Options")
    clear_app = st.button("🔄 Clear App")
    translate = st.checkbox("🌍 Translate to French")
    word_freq = st.checkbox("📊 Show Word Frequency")
    st.markdown("---")

if clear_app:
    st.experimental_rerun()

if st.button("🎬 Download & Transcribe"):
    if video_url:
        try:
            with st.spinner("📥 Downloading audio..."):
                audio_file = download_youtube_audio(video_url)

            st.audio(audio_file, format="audio/mp3", start_time=0)

            # Load Whisper model
            with st.spinner("📝 Transcribing audio..."):
                model = whisper.load_model("tiny")
                result = model.transcribe(audio_file)
                transcript = result["text"]

            st.success("✅ Transcription completed!")
            st.subheader("📜 Transcript")
            st.text_area("", transcript, height=300)

            # Word Frequency Option
            if word_freq:
                st.subheader("📊 Most Frequent Words")
                word_counts = get_word_frequency(transcript)
                st.write(word_counts)

            # Translation Option
            if translate:
                st.subheader("🌍 Translated Transcript (French)")
                translated_text = translate_text(transcript, "fr")
                st.write(translated_text)

            # Save transcript as Word file
            docx_path = save_transcript_to_docx(transcript)

            # Download button for transcript
            with open(docx_path, "rb") as file:
                st.download_button(
                    label="📥 Download Transcript (Word)",
                    data=file,
                    file_name="transcript.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a valid YouTube URL.")

# Footer
st.markdown("---")
st.markdown("📌 **Developed by Ali Haider** | Powered by OpenAI Whisper & Streamlit")
