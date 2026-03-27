import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import Config
from src.transcribe import AudioTranscriber
from src.summarize import TextSummarizer
from src.qa_generator import QAGenerator
from src.utils import export_to_pdf, export_to_docx, export_to_txt

# Load environment variables
load_dotenv()

# Configure Streamlit
st.set_page_config(
    page_title="AI Lecture Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "qa_results" not in st.session_state:
    st.session_state.qa_results = None

# Header
st.title("🎓 AI Lecture Assistant")
st.markdown("Transform your lectures into comprehensive study materials with AI")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    llm_provider = st.radio(
        "Select LLM Provider",
        options=["OpenAI", "Ollama (Local)"],
        help="Choose between cloud-based OpenAI or local Ollama"
    )
    
    if llm_provider == "OpenAI":
        api_key = st.text_input("OpenAI API Key", type="password", key="openai_key")
    
    language = st.selectbox(
        "Lecture Language",
        options=["English", "Spanish", "French", "German", "Arabic"],
        help="Select the primary language of your lecture"
    )
    
    enable_diarization = st.checkbox(
        "Enable Speaker Diarization",
        value=False,
        help="Identify and separate different speakers"
    )
    
    summary_style = st.radio(
        "Summary Style",
        options=["Brief (Key Points)", "Detailed (Full Summary)", "Bullet Points"],
        help="Choose how you want your summary formatted"
    )

# Main interface with tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload & Transcribe",
    "📝 Transcript Viewer",
    "📊 Analysis",
    "📥 Export"
])

# Tab 1: Upload & Transcribe
with tab1:
    st.header("Upload Lecture Audio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Select audio file (MP3, WAV, M4A)",
            type=["mp3", "wav", "m4a", "ogg"],
            help="Maximum file size: 500MB"
        )
    
    with col2:
        st.metric("Max File Size", "500MB")
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Save uploaded file temporarily
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / uploaded_file.name
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Transcribe button
        if st.button("🎯 Start Transcription", key="transcribe_btn", use_container_width=True):
            with st.spinner("🔄 Transcribing audio... This may take a few minutes"):
                try:
                    config = Config(
                        openai_api_key=api_key if llm_provider == "OpenAI" else None,
                        language=language,
                        enable_diarization=enable_diarization
                    )
                    transcriber = AudioTranscriber(config)
                    result = transcriber.transcribe(str(temp_file_path))
                    
                    st.session_state.transcription = result
                    st.success("✅ Transcription completed!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error during transcription: {str(e)}")

# Tab 2: Transcript Viewer
with tab2:
    st.header("📝 Transcript Viewer")
    
    if st.session_state.transcription:
        # Display transcript with timestamps
        st.subheader("Full Transcript")
        
        transcript_text = st.session_state.transcription.get("text", "")
        segments = st.session_state.transcription.get("segments", [])
        
        # Search functionality
        search_term = st.text_input("🔍 Search in transcript:")
        
        if segments:
            st.write("**Transcript with Timestamps:**")
            for segment in segments:
                timestamp = segment.get("start", 0)
                text = segment.get("text", "")
                
                # Highlight search term if provided
                if search_term and search_term.lower() in text.lower():
                    text = text.replace(
                        search_term,
                        f":yellow[{search_term}]"
                    )
                
                st.write(f"**{timestamp:.1f}s** - {text}")
        else:
            st.write(transcript_text)
        
        # Copy to clipboard
        if st.button("📋 Copy Transcript"):
            st.write("Copied to clipboard!")
    else:
        st.info("📌 Upload and transcribe an audio file first.")

# Tab 3: Analysis
with tab3:
    st.header("📊 Analysis & Processing")
    
    if st.session_state.transcription:
        col1, col2 = st.columns(2)
        
        # Summarization
        with col1:
            st.subheader("📋 Summary Generation")
            if st.button("Generate Summary", key="summarize_btn", use_container_width=True):
                with st.spinner("✍️ Generating summary..."):
                    try:
                        config = Config(
                            openai_api_key=api_key if llm_provider == "OpenAI" else None,
                            language=language,
                            llm_provider=llm_provider.lower()
                        )
                        summarizer = TextSummarizer(config)
                        summary = summarizer.summarize(
                            st.session_state.transcription["text"],
                            style=summary_style
                        )
                        st.session_state.summary = summary
                        st.success("✅ Summary generated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            if st.session_state.summary:
                st.write(st.session_state.summary)
        
        # Q&A Generation
        with col2:
            st.subheader("❓ Q&A Generation")
            if st.button("Generate Q&A", key="qa_btn", use_container_width=True):
                with st.spinner("🤔 Generating questions..."):
                    try:
                        config = Config(
                            openai_api_key=api_key if llm_provider == "OpenAI" else None,
                            language=language,
                            llm_provider=llm_provider.lower()
                        )
                        qa_gen = QAGenerator(config)
                        qa_results = qa_gen.generate_qa(st.session_state.transcription["text"])
                        st.session_state.qa_results = qa_results
                        st.success("✅ Q&A generated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            if st.session_state.qa_results:
                for i, qa in enumerate(st.session_state.qa_results.get("qa_pairs", [])[:5]):
                    with st.expander(f"Q{i+1}: {qa['question'][:50]}..."):
                        st.write(f"**Answer:** {qa['answer']}")
    else:
        st.info("📌 Transcribe audio first to enable analysis.")

# Tab 4: Export
with tab4:
    st.header("📥 Export Results")
    
    if st.session_state.transcription or st.session_state.summary:
        export_format = st.radio("Select export format:", ["PDF", "DOCX", "TXT"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export Transcript", use_container_width=True):
                try:
                    if export_format == "PDF":
                        file_data = export_to_pdf(
                            st.session_state.transcription.get("text", ""),
                            "Lecture Transcript"
                        )
                        st.download_button(
                            "Download Transcript (PDF)",
                            file_data,
                            file_name="transcript.pdf",
                            mime="application/pdf"
                        )
                    elif export_format == "DOCX":
                        file_data = export_to_docx(
                            st.session_state.transcription.get("text", ""),
                            "Lecture Transcript"
                        )
                        st.download_button(
                            "Download Transcript (DOCX)",
                            file_data,
                            file_name="transcript.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    else:
                        file_data = export_to_txt(
                            st.session_state.transcription.get("text", "")
                        )
                        st.download_button(
                            "Download Transcript (TXT)",
                            file_data,
                            file_name="transcript.txt",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
        
        with col2:
            if st.button("📋 Export Summary", use_container_width=True):
                if st.session_state.summary:
                    try:
                        if export_format == "PDF":
                            file_data = export_to_pdf(
                                st.session_state.summary,
                                "Lecture Summary"
                            )
                            st.download_button(
                                "Download Summary (PDF)",
                                file_data,
                                file_name="summary.pdf",
                                mime="application/pdf"
                            )
                        elif export_format == "DOCX":
                            file_data = export_to_docx(
                                st.session_state.summary,
                                "Lecture Summary"
                            )
                            st.download_button(
                                "Download Summary (DOCX)",
                                file_data,
                                file_name="summary.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        else:
                            file_data = export_to_txt(st.session_state.summary)
                            st.download_button(
                                "Download Summary (TXT)",
                                file_data,
                                file_name="summary.txt",
                                mime="text/plain"
                            )
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
                else:
                    st.warning("⚠️ Generate a summary first.")
        
        with col3:
            if st.button("❓ Export Q&A", use_container_width=True):
                if st.session_state.qa_results:
                    try:
                        qa_text = "\n\n".join([
                            f"Q: {qa['question']}\nA: {qa['answer']}"
                            for qa in st.session_state.qa_results.get("qa_pairs", [])
                        ])
                        
                        if export_format == "PDF":
                            file_data = export_to_pdf(qa_text, "Lecture Q&A")
                            st.download_button(
                                "Download Q&A (PDF)",
                                file_data,
                                file_name="qa.pdf",
                                mime="application/pdf"
                            )
                        elif export_format == "DOCX":
                            file_data = export_to_docx(qa_text, "Lecture Q&A")
                            st.download_button(
                                "Download Q&A (DOCX)",
                                file_data,
                                file_name="qa.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        else:
                            file_data = export_to_txt(qa_text)
                            st.download_button(
                                "Download Q&A (TXT)",
                                file_data,
                                file_name="qa.txt",
                                mime="text/plain"
                            )
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
                else:
                    st.warning("⚠️ Generate Q&A first.")
    else:
        st.info("📌 Transcribe audio and generate content first.")

# Footer
st.markdown("---")
st.markdown(
    "🎓 **AI Lecture Assistant** | Built with Streamlit, Whisper & LangChain | "
    "[GitHub](https://github.com/Tarekfawzy/AI-LECTURE-ASSISTANT)"
)
