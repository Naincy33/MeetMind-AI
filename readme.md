# 🚀 MeetMind AI

### Intelligent Meeting Intelligence Platform powered by Generative AI

MeetMind AI is an AI-powered meeting intelligence platform that transforms long meetings, lectures, podcasts and YouTube videos into structured knowledge.

The platform automatically transcribes audio, generates executive summaries, extracts action items, key decisions and open questions, enables context-aware AI chat using Retrieval-Augmented Generation (RAG), and exports professional PDF reports through an elegant Streamlit dashboard.

---

## ✨ Features

- 🎙️ Automatic Speech-to-Text using Whisper
- 🧠 AI Generated Meeting Title
- 📝 Executive Summary
- ✅ Action Items Extraction
- 📌 Key Decisions Extraction
- ❓ Open Questions Extraction
- 💬 AI Chat with Meeting (RAG)
- 📄 Professional PDF Report Export
- 📊 Meeting Statistics Dashboard
- 🎨 Premium Dark UI
- 📺 YouTube Video Support
- 📁 Local Audio File Support

---

## 🖥️ Dashboard

### Meeting Overview

- AI Generated Title
- Reading Time
- Transcript Statistics
- Language Detection

### AI Analysis

- Executive Summary
- Action Items
- Key Decisions
- Open Questions

### RAG Chat

Ask anything about your meeting.

Examples:

- Summarize the discussion.
- What were the key features?
- What decisions were made?
- Explain this topic in simple words.

### PDF Export

Generate a professional AI Meeting Report with:

- Meeting Title
- Executive Summary
- Action Items
- Key Decisions
- Open Questions
- Full Transcript

---

## 🏗️ Project Architecture

```
User Input
      │
      ▼
Audio Extraction
      │
      ▼
Whisper Transcription
      │
      ▼
LLM Analysis (Mistral AI)
      │
      ├── Title Generation
      ├── Summary
      ├── Action Items
      ├── Key Decisions
      └── Open Questions
      │
      ▼
Embedding Generation
      │
      ▼
ChromaDB Vector Store
      │
      ▼
LangChain RAG
      │
      ▼
Interactive AI Chat
      │
      ▼
PDF Report Generation
```

---

## ⚙️ Tech Stack

### AI & LLM

- Whisper
- Mistral AI
- LangChain (LCEL)
- HuggingFace Embeddings

### Vector Database

- ChromaDB

### Backend

- Python

### Frontend

- Streamlit

### Report Generation

- ReportLab

### Media Processing

- yt-dlp
- FFmpeg

---

## 📂 Project Structure

```
MeetMind-AI/
│
├── app.py
├── main.py
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   ├── audio_processor.py
│   └── pdf_generator.py
│
├── downloads/
├── vector_db/
├── Requirements.txt
└── README.md
```

---

## 🚀 Installation

```bash
git clone <repository-url>

cd MeetMind-AI

pip install -r Requirements.txt
```

Create a `.env` file

```env
MISTRAL_API_KEY=YOUR_API_KEY
```

Run the application

```bash
streamlit run app.py
```

---

## 💡 Future Enhancements

- DOCX Export
- Speaker Diarization
- Meeting History
- Cloud Deployment
- Team Collaboration

---

## 👩‍💻 Developed By

**Naincy**

B.Tech Computer Science Engineering  
B.M.S. College of Engineering

---

## ⭐ If you found this project useful, consider giving it a star!