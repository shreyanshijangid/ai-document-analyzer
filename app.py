import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="AI Document Analyzer", page_icon="📄", layout="wide")

# Custom CSS for card-style containers
st.markdown("""
<style>
    /* Card style for metrics that adapts to light/dark mode */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Slight adjustments to tabs that adapt to light/dark mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        background-color: var(--secondary-background-color);
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom: 2px solid var(--primary-color);
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
