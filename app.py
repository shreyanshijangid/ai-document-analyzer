import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="AI Document Analyzer", page_icon="📄", layout="wide")

# Custom CSS for optimized glassmorphism and background
st.markdown("""
<style>
    /* Static Gradient Background to improve performance */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }

    /* Optimized Glassmorphism for sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 32, 39, 0.7) !important;
        backdrop-filter: blur(8px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Metric Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.3);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background-color: transparent;
        color: rgba(255,255,255,0.7) !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-bottom: none !important;
        color: white !important;
    }

    /* Expanders and Chat messages (No blur for performance) */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    /* Inputs and Buttons */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, [data-baseweb="select"] > div {
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }

    .stButton button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Global text colors */
    h1, h2, h3, h4, p, label, .stMarkdown {
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states for exporting and history
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "key_points" not in st.session_state:
    st.session_state.key_points = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for configuration and exports
with st.sidebar:
    # App Logo
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>📄 AI Doc Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
    st.markdown("Get your API key from [Google AI Studio](https://aistudio.google.com/).")
    
    st.markdown("---")
    st.header("💾 Export Results")
    st.write("Download your analysis below.")
    
    # Generate download content dynamically based on session state
    download_content = "AI DOCUMENT ANALYZER - EXPORTED RESULTS\n"
    download_content += "="*40 + "\n\n"
    if st.session_state.summary:
        download_content += "SUMMARY:\n" + "-"*8 + "\n" + st.session_state.summary + "\n\n"
    if st.session_state.key_points:
        download_content += "KEY POINTS:\n" + "-"*11 + "\n" + st.session_state.key_points + "\n\n"
    if st.session_state.chat_history:
        download_content += "Q&A HISTORY:\n" + "-"*12 + "\n"
        for msg in st.session_state.chat_history:
            role = "User" if msg["role"] == "user" else "AI"
            download_content += f"{role}: {msg['content']}\n\n"
            
    st.download_button(
        label="📥 Download All Results (.txt)",
        data=download_content,
        file_name="document_analysis_results.txt",
        mime="text/plain",
        use_container_width=True
    )
    
# Main page content
st.title("📄 AI Document Analyzer")
st.markdown("""
Upload your documents and let the power of Google Gemini analyze them for you.
Provide your API key in the sidebar to get started.
""")

# Initialize Gemini if API key is provided
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Dynamically fetch available models to prevent 404 errors
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name.replace("models/", ""))
        except Exception as e:
            st.sidebar.error(f"Error fetching models: {e}")
            available_models = ["gemini-1.5-flash", "gemini-pro"]
            
        if not available_models:
            st.sidebar.warning("No models found for your API key. Defaulting to gemini-pro.")
            available_models = ["gemini-pro"]
            
        # Model Selection in Sidebar
        st.sidebar.markdown("---")
        st.sidebar.header("🤖 Model Selection")
        selected_model = st.sidebar.selectbox("Available Models (Fetched from API)", available_models)
        
        # Initialize the model
        model = genai.GenerativeModel(selected_model)
        
        # File uploader
        uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])
        
        if uploaded_file is not None:
            document_text = ""
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            try:
                # Handle PDF files
                if uploaded_file.name.lower().endswith(".pdf"):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    num_pages = len(pdf_reader.pages)
                    
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            document_text += extracted + "\n"
                            
                # Handle TXT files
                elif uploaded_file.name.lower().endswith(".txt"):
                    document_text = uploaded_file.read().decode("utf-8")
                    
                word_count = len(document_text.split())
                
                # Display Document Metadata Cards
                st.markdown("### 📊 Document Metadata")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Filename", uploaded_file.name)
                with col2:
                    st.metric("File Size", f"{file_size_mb:.2f} MB")
                with col3:
                    st.metric("Word Count", f"{word_count:,}")
                
                # Show preview in an expander
                with st.expander("🔍 Document Preview"):
                    preview_text = document_text[:500] + "..." if len(document_text) > 500 else document_text
                    st.text(preview_text)
                    
                # Analysis section
                st.markdown("---")
                st.subheader("💡 Document Analysis")
                
                # Check if document has text
                if not document_text.strip():
                    st.warning("The uploaded document appears to be empty or text could not be extracted.")
                else:
                    tab1, tab2, tab3 = st.tabs(["📝 Summarize", "🎯 Extract Key Points", "💬 Q&A"])
                    
                    with tab1:
                        if st.button("Generate Summary"):
                            with st.spinner("Analyzing document and generating summary..."):
                                try:
                                    prompt = f"Summarize this document in 3-5 clear paragraphs:\n\n{document_text}"
                                    response = model.generate_content(prompt)
                                    st.session_state.summary = response.text
                                except Exception as e:
                                    st.error(f"An error occurred during summarization: {str(e)}")
                        
                        # Display summary from session state if it exists
                        if st.session_state.summary:
                            st.markdown(st.session_state.summary)
                                    
                    with tab2:
                        if st.button("Extract Key Points"):
                            with st.spinner("Extracting key insights..."):
                                try:
                                    prompt = f"Extract exactly 10 bullet point key insights from this document:\n\n{document_text}"
                                    response = model.generate_content(prompt)
                                    st.session_state.key_points = response.text
                                except Exception as e:
                                    st.error(f"An error occurred during extraction: {str(e)}")
                                    
                        # Display key points from session state if they exist
                        if st.session_state.key_points:
                            st.markdown(st.session_state.key_points)

                    with tab3:
                        st.subheader("Ask questions about your document")
                            
                        # Display chat history
                        for message in st.session_state.chat_history:
                            with st.chat_message(message["role"]):
                                st.markdown(message["content"])
                                
                        # Chat input
                        user_question = st.chat_input("Ask a question about the document...")
                        if user_question:
                            # Add user message to history and display it
                            st.session_state.chat_history.append({"role": "user", "content": user_question})
                            with st.chat_message("user"):
                                st.markdown(user_question)
                                
                            # Generate response
                            with st.chat_message("assistant"):
                                with st.spinner("Thinking..."):
                                    try:
                                        prompt = f"Based on this document:\n\n{document_text}\n\nAnswer this question: {user_question}"
                                        response = model.generate_content(prompt)
                                        
                                        st.markdown(response.text)
                                        # Add response to history
                                        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                                    except Exception as e:
                                        st.error(f"An error occurred: {str(e)}")
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
    except Exception as e:
        st.error(f"Error configuring API Key: {str(e)}")
else:
    st.info("Please enter your Google Gemini API Key in the sidebar to proceed.")
