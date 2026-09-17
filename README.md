# FinNews AI — Financial News Simplifier & Multilingual Intelligence

<p align="center">
  <img src="static/images/robot-mascot.svg" width="120" alt="FinNews AI Mascot" />
</p>

<p align="center">
  <strong>Transforming dense Wall Street jargon and market volatility reports into clear, actionable intelligence.</strong>
</p>

<p align="center">
  <a href="https://finnews-ai-23dc9.web.app"><img src="https://img.shields.io/badge/Live_Demo-finnews--ai.web.app-blue?style=for-the-badge&logo=firebase" alt="Live Demo"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Google_Gemini-AI_Inside-4285F4?style=for-the-badge&logo=google" alt="Google Gemini AI">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License MIT">
</p>

---

## 🌐 Live Application

- **Live Production URL**: [https://finnews-ai-23dc9.web.app](https://finnews-ai-23dc9.web.app)
- **Local Development Server**: `http://127.0.0.1:8000`
- **Swagger Interactive API Docs**: `http://127.0.0.1:8000/docs`

---

## 🌟 Key Features

### 1. 📰 Real-Time Financial News Simplification
- Live financial headlines across Fed & Macroeconomics, Tech Stocks & AI, Crypto & Web3, Commodities, and Banking.
- Transforms complex, jargon-heavy articles into:
  - 📌 **What Happened**: Factual, distilled event breakdown.
  - 💡 **Why It Matters**: Practical relevance to household budgets, mortgage rates, and portfolios.
  - 📊 **Market & Dollar Impact**: Movements across equity indices, bond yields, and commodity curves.
  - ⚡ **Key Takeaways**: Bullet points highlighting crucial figures and metrics.

### 2. 🌐 Multilingual Intelligence (English, Hindi, Marathi, Spanish, French, German)
- Fully localized UI and content in **English**, **हिन्दी (Hindi)**, **मराठी (Marathi)**, **Español (Spanish)**, **Français (French)**, and **Deutsch (German)**.
- Switching language translates news headlines, simplified summaries, takeaways, and market mood badges dynamically.

### 3. 🔊 Voice Audio Narration Engine
- One-click audio breakdown button (🔊) on every article card and inside the detailed breakdown modal.
- Multi-tier playback:
  - **Localhost**: High-fidelity `/api/tts` audio streaming.
  - **Static Web Hosting (Firebase)**: Sentence-chunked Google TTS audio streaming directly in HTML5 Audio for seamless narration.
  - **Browser Web Speech API**: Automated fallback to native system speech voices (`hi-IN`, `mr-IN`, `en-US`, `es-ES`, `fr-FR`, `de-DE`).

### 4. 🤖 FinBot — Personal Financial AI Assistant
- Embedded AI chatbot powered by Google Gemini (with multi-model quota fallback).
- Answers questions regarding economic concepts, definitions, market hours, and comparisons (e.g. *Stocks vs Bonds*, *ETFs vs Mutual Funds*, *Bitcoin vs Gold*, *Rule of 72*).
- Adapts and replies in the user's active language (English, Hindi, Marathi).

### 5. 📖 Financial Jargon Buster & Glossary
- Detects 60+ terms (*Quantitative Tightening*, *Hawkish*, *EBITDA*, *Yield Curve Inversion*, *Repo Rate*, *Basis Points*).
- Hover tooltips and a searchable financial dictionary modal with real-world examples.

### 6. 📊 Sentiment Analysis & Market Mood Gauge
- Real-time Bullish (▲), Bearish (▼), and Neutral (◼) scoring.
- Visual market sentiment score (0–100) and localized mood tags (*Bullish Greed*, *Bearish Fear*, *तेजी / आशावादी*, *मंदी / सावध*).

---

## 🏗️ Architecture & Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, HTTPX, Pydantic v2
- **AI & LLM**: Google Gemini API (`gemini-flash-lite-latest`, `gemini-3.5-flash-lite`) with heuristic offline NLP fallback
- **Frontend**: Vanilla JavaScript (ES6+), CSS3 with Glassmorphism, Semantic HTML5
- **Hosting & Deployment**: Firebase Hosting (Static CDN) & FastAPI daemon (Localhost/Cloud)
- **Audio & Speech**: Google TTS Audio Stream + Web Speech API (`SpeechSynthesis`)

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/FinNews-AI.git
cd FinNews-AI
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Add your optional API keys:
- `GEMINI_API_KEY`: Google Gemini API key ([Get free key](https://aistudio.google.com/))
- `NEWS_API_KEY`: NewsAPI key ([Get key](https://newsapi.org/))

*(Note: The application has built-in curated intelligence and works out of the box even without external keys!)*

### 5. Run the Application
```bash
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 📂 Repository Structure

```
FinNews-AI/
├── app/
│   ├── config.py              # Settings & environment variables
│   ├── main.py                # FastAPI endpoints & static routing
│   ├── models/
│   │   └── schemas.py         # Pydantic data schemas
│   └── services/
│       ├── ai_service.py      # Gemini & heuristic text simplifier
│       ├── auth_service.py    # Authentication & guest profile session
│       ├── chat_service.py    # FinBot conversation engine
│       ├── glossary_service.py# 60+ financial terms dictionary
│       ├── news_service.py    # Live RSS, curated feeds & market overview
│       ├── sentiment_service.py# Sentiment scoring & sector classifier
│       └── translation_service.py# Multilingual dictionary & dynamic translator
├── data/
│   ├── translations_cache.json# Local translations cache
│   └── users.json             # Local users storage
├── public/                    # Production static build for Firebase Hosting
│   ├── index.html
│   └── static/
├── static/
│   ├── css/
│   │   └── style.css          # Responsive styling & themes
│   ├── images/
│   │   └── robot-mascot.svg   # Vector mascot illustration
│   └── js/
│       └── app.js             # Client app controller, audio & fallbacks
├── templates/
│   └── index.html             # Server-rendered Jinja2 template
├── .env.example               # Environment variables template
├── .firebaserc                # Firebase project configuration
├── firebase.json              # Firebase Hosting configuration
├── LICENSE                    # MIT License
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── run.py                     # Server launch script
└── test_app.py                # Automated endpoint test suite
```

---

## 🧪 Testing

Run the test suite to verify all endpoints, translation services, and TTS synthesis:
```bash
python -m pytest test_app.py
# or
python test_app.py
```

---

## 👨‍💻 Author & Developer

**Developed with ❤️ by Yogesh Jadhao**
- **GitHub**: [yogeshjadhao](https://github.com/yogeshjadhao) • [Profile](https://share.google/kHmdJYelhqUdcXryi)
- **LinkedIn**: [Yogesh Jadhao](https://www.linkedin.com/in/yogesh-jadhao-a88a22383)
- **Email**: [yogeshjadhao0345@gmail.com](mailto:yogeshjadhao0345@gmail.com)
- **Instagram**: [@yogesh._.jadhao](https://www.instagram.com/yogesh._.jadhao)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
