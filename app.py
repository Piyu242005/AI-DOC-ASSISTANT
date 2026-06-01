import streamlit as st
from google import genai
import os
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()  # Load GEMINI_API_KEY from .env file

# Page Title
st.title("📄 AI Document Assistant")
st.write("Upload a PDF and ask questions about the document using Generative AI.")

# Sidebar
st.sidebar.title("About")
st.sidebar.write(
    "This demo shows how Generative AI can answer questions from documents using Google Gemini."
)
st.sidebar.write("Model: Gemini 2.0 Flash")

# Gemini API Key input (fallback to env variable)
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to continue.")
    st.stop()

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:

    st.success("Document uploaded successfully")

    reader = PdfReader(uploaded_file)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    # limit text length
    text = text[:15000]

    # Preview document
    with st.expander("Preview Document Text"):
        st.write(text[:2000] + "...")

    # Summarize button
    if st.button("Summarize Document"):
        question = "Provide a concise summary of this document."
    else:
        question = None

    # Question form
    with st.form("question_form"):
        user_question = st.text_input("Ask a question about the document")
        submit_button = st.form_submit_button("Ask AI")

        if submit_button:
            question = user_question

    if question:

        prompt = f"""Answer the question using the document below.

Document:
{text}

Question:
{question}
"""

        try:
            with st.spinner("AI is analyzing the document..."):
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                answer = response.text

            # Clean response display
            st.markdown("### AI Response")
            st.markdown(answer)

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                st.error(
                    "⚠️ **Quota Exceeded (429):** Your Gemini API free tier limit has been reached.\n\n"
                    "**Options to fix this:**\n"
                    "- Wait a few minutes and try again\n"
                    "- Enable billing at [Google AI Studio](https://aistudio.google.com)\n"
                    "- Use a different API key"
                )
            else:
                st.error(f"❌ An error occurred: {error_msg}")