# VaaniBridge AI - Marathi to English Voice Intelligence Platform
 
VaaniBridge ("Vaani" = voice, "Bridge" = connection) is a full-stack AI application that understands spoken Marathi and responds in English combining speech recognition, machine translation, and AI-generated answers into a single, production-style pipeline.
 
The app supports **two core capabilities**:
 
**1. Translation** - a Marathi sentence spoken by the user is translated into English.
> Marathi: "मला उद्या पुण्याला जायचं आहे."
> English: "I want to go to Pune tomorrow."
 
**2. Question Answering** - if the user asks a question in Marathi, the app doesn't just translate the question - it generates and returns the **answer**, in English.
> Marathi question: "पुण्यात कोणती प्रसिद्ध ठिकाणं आहेत?"
> English answer: "Some famous places in Pune include Shaniwar Wada, Aga Khan Palace, and Sinhagad Fort."
 
Both text and optional AI-generated English audio playback are supported for the output.
 
---
 
## ✨ Features
 
| Feature | Purpose |
|---|---|
| Marathi voice recording | Capture spoken input from the browser microphone |
| Speech recognition | Convert Marathi speech into text |
| Marathi → English translation | Translate Marathi sentences into accurate, context-aware English |
| Marathi question → English answer | Detect when input is a question and generate an AI answer in English, rather than a literal translation |
| English pronunciation | Read the translated text or answer aloud using AI-generated speech |
| Translation/answer history | Save and revisit previous results |
| Confidence & quality checks | Flag potentially low-confidence translations or answers |
| Modern web interface | Clean, responsive frontend for recording and viewing results |
| API documentation | Auto-generated interactive docs via FastAPI |
 
---
 
## 🏗️ Architecture
 
This project uses a **multi-stage pipeline** rather than direct audio-to-English translation:
 
1. **Speech → Marathi text** — Transcribe what the user actually said, preserving the original language for review and correction.
2. **Marathi text → Intent check** — Determine whether the input is a plain sentence (translate it) or a question (answer it).
3. **Text → English output** — Either translate the Marathi text into English, or generate an AI answer to the Marathi question, returned in English.
4. **English text → Voice** — Optionally generate spoken English audio from the output.
**Why this design?**
It allows the original Marathi transcript to be shown to the user, supports manual correction, enables quality evaluation, and lets the app behave like an assistant (answering questions) rather than a pure translator — at the cost of an extra processing step compared to direct audio translation.
 
### Data flow
 
```
Browser mic → Audio file → FastAPI backend → OpenAI API (speech-to-text)
    → Marathi text → GPT (translate OR answer, based on input type) → English text
    → OpenAI API (text-to-speech, optional) → Audio playback
```
 
---
 
## 🛠️ Tech Stack
 
- **Python** - core backend language
- **FastAPI** - REST API framework with built-in request validation and auto-generated docs
- **OpenAI API** - speech-to-text, translation, and text-to-speech
- **HTML, CSS, JavaScript** — frontend interface and microphone/API integration
- **SQLite** - lightweight storage for translation history (migratable to PostgreSQL for production)
---
  
## 🚀 Getting Started
 
### Prerequisites
- Python 3.10+
- An OpenAI API key
### Setup
 
1. Clone the repository
```bash
   git clone https://github.com/aruna-arjun/VaaniBridge-AI.git
   cd VaaniBridge-AI
```
 
2. Set up the backend environment
```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
```
 
3. Add your OpenAI API key
   Create a `.env` file inside `backend/` (see `.env.example` for the expected format):
```
   OPENAI_API_KEY=your_key_here
```
 
4. Run the backend
```bash
   uvicorn main:app --reload
```
 
5. Open `frontend/index.html` in your browser (or serve it via a local dev server).
---
 
## 🔮 Roadmap
 
- [ ] Translation confidence scoring
- [ ] Glossary support for domain-specific terms
- [ ] Migrate history storage from SQLite to PostgreSQL
- [ ] Deploy backend and frontend to a public host
- [ ] Add automated tests for API endpoints
---
 
## ⚠️ Note
 
This is a learning/portfolio project built to practice full-stack development and AI API integration end-to-end from voice capture to backend processing to deployment.