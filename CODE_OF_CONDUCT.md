# 📋 Code of Conduct — NeuraFlow AI

> Intelligent Multi-LLM Document Agent Platform

---

## 🧠 About the Project

**NeuraFlow AI** is a production-grade AI platform that lets you upload any PDF document and ask questions about it using **multiple Large Language Models simultaneously**.

Instead of relying on a single AI provider, NeuraFlow uses an **Intelligent Agent Router** that:
- Classifies the type of your question (coding, reasoning, general, etc.)
- Automatically selects the **best-suited LLM** for that task
- Falls back to the **next available provider** if one fails or hits a quota limit

### 🤖 Models Used
| Provider | Model | Best For |
| :--- | :--- | :--- |
| ⚡ **Groq** | LLaMA 3.1 8B | Coding & fast tasks |
| 🔵 **Google Gemini** | Gemini 1.5 Flash | General Q&A |
| 🌐 **OpenRouter** | LLaMA 3 8B | Reasoning & analysis |
| 🤗 **Hugging Face** | Zephyr 7B | Research & experimentation |

### ✨ Key Capabilities
- 📄 PDF document upload and text extraction
- 🔀 Intelligent multi-LLM routing with automatic fallback
- 🧠 AI Decision Panel showing why a model was chosen
- 🔒 Secure API key management (local `.env` + Streamlit Cloud secrets)
- 🎨 Modern dark-themed Streamlit UI

---

## 🚀 How to Run the Project

### Step 1 — Clone the Repository
```bash
git clone https://github.com/Piyu242005/AI-DOC-ASSISTANT.git
cd AI-DOC-ASSISTANT
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure API Keys
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY="your_google_gemini_key"
GROQ_API_KEY="your_groq_key"
OPENROUTER_API_KEY="your_openrouter_key"
HUGGINGFACE_API_KEY="your_huggingface_key"
```

> 💡 You need at least **one** API key to run the app. The fallback system will skip providers with missing keys.

### Step 5 — Run the App
```bash
python -m streamlit run app.py
```

Then open your browser at **http://localhost:8501**

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push your code to GitHub (**do NOT push your `.env` file**)
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and connect your repo
3. In **App Settings → Secrets**, add:
```toml
GEMINI_API_KEY = "your_key"
GROQ_API_KEY = "your_key"
OPENROUTER_API_KEY = "your_key"
HUGGINGFACE_API_KEY = "your_key"
```

The app auto-detects whether it's running locally (uses `.env`) or on the cloud (uses Streamlit Secrets).

---

## 🤝 Contribution Guidelines

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository and create a feature branch
2. **Write clean code** — all PRs are checked by our CI pipeline (`black`, `isort`, `flake8`)
3. **Test your changes** before opening a pull request
4. **Document** any new provider or feature you add
5. **Never commit** API keys, secrets, or `.env` files

### Code Style
This project enforces:
- [`black`](https://black.readthedocs.io/) for code formatting
- [`isort`](https://pycqa.github.io/isort/) for import ordering
- [`flake8`](https://flake8.pycqa.org/) for style and error checking (max line length: 100)

Run these before committing:
```bash
python -m black .
python -m isort .
python -m flake8 . --max-line-length=100 --ignore=E203,W503
```

---

## 🛡️ Security & Privacy

- **API keys** must never be pushed to GitHub
- `.env` and `.env.local` are listed in `.gitignore`
- The CI pipeline runs an automatic **secret scanning** check on every push
- Report any security vulnerabilities privately via GitHub Issues

---

## 📬 Contact

**Piyush Ramteke** — Data Scientist | AI Engineer | Python Developer

[![GitHub](https://img.shields.io/badge/GitHub-Piyu242005-181717?style=flat-square&logo=github)](https://github.com/Piyu242005)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-piyush--ramteke-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/piyush-ramteke)
[![Hugging Face](https://img.shields.io/badge/HuggingFace-Piyu242005-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co/Piyu242005)

---

<div align="center">
  <sub>Built with ❤️ using Python, Streamlit, and modern Generative AI · NeuraFlow AI</sub>
</div>
