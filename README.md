# 📄 AI Document Analyzer

AI Document Analyzer is a Streamlit web application powered by Google Gemini. Upload PDF or TXT files to instantly generate comprehensive summaries, extract key bullet-point insights, and interact with your documents through an intelligent Q&A chat interface. Features include dynamic model selection, adaptive UI, and downloadable analysis exports.

## ✨ Features

- **Document Parsing:** Seamlessly upload and extract text from both `.pdf` (via PyPDF2) and `.txt` files.
- **AI Summarization:** Generate clear, 3-5 paragraph summaries of your documents with a single click.
- **Key Insights Extraction:** Automatically pull exactly 10 high-value bullet points from your uploaded text.
- **Interactive Q&A Chat:** Talk to your document! Ask specific questions and receive context-aware answers using a conversational UI.
- **Dynamic Model Selection:** Securely queries the Google API to fetch the exact Gemini models available to your specific API key (e.g., `gemini-1.5-flash`, `gemini-pro`), preventing compatibility errors.
- **Export Results:** Download your generated summary, key points, and full Q&A chat history as a formatted `.txt` file.
- **Adaptive UI:** Custom CSS styling that looks beautiful in both Light and Dark mode.

## 🚀 Installation & Setup

### Prerequisites
Make sure you have Python 3.8+ installed on your machine. You will also need a free [Google Gemini API Key](https://aistudio.google.com/).

### Local Setup

1. **Clone the repository (or download the files):**
   ```bash
   git clone https://github.com/yourusername/ai-document-analyzer.git
   cd ai-document-analyzer
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

4. **Use the App:**
   - Open your browser to the local URL provided by Streamlit (usually `http://localhost:8501`).
   - Paste your Google Gemini API Key in the sidebar.
   - Upload a document and start analyzing!

## 📦 Dependencies

- `streamlit`: For building the interactive web interface.
- `google-generativeai`: The official Google SDK for interacting with Gemini models.
- `PyPDF2`: For parsing and extracting text from PDF documents.
- `python-dotenv`: For managing environment variables (optional, for local development).

## 🌐 Deployment

This application is ready to be deployed on **Streamlit Community Cloud**:
1. Push this code to a public GitHub repository.
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **New app**, select your repository, and set the main file path to `app.py`.
4. Click **Deploy!**

Users will be able to supply their own API keys via the sidebar UI, making your deployed app secure and publicly shareable.
