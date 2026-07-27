![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)
![Whisper](https://img.shields.io/badge/OpenAI-Whisper-green)
![LangChain](https://img.shields.io/badge/LangChain-RAG-success)
![Mistral AI](https://img.shields.io/badge/Mistral-AI-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

# 🧠 MeetMind AI – Intelligent Meeting Analysis & Knowledge Assistant

Transform YouTube videos or meeting recordings into searchable knowledge using AI.

MeetMind AI automatically transcribes audio, generates concise summaries, extracts action items, identifies key decisions, answers questions through RAG (Retrieval-Augmented Generation), and exports professional meeting reports as PDF.

---

## 🚀 Features

- 🎥 Analyze YouTube videos
- 🎙️ Speech-to-Text using OpenAI Whisper
- 📝 AI-generated Meeting Summary
- 📌 Automatic Meeting Title
- ✅ Action Item Extraction
- 📍 Key Decision Detection
- ❓ Open Question Identification
- 💬 Chat with your Meeting (RAG)
- 📄 Export Professional PDF Report
- 🎨 Modern Dark Dashboard UI

---

## 🏗️ System Architecture

```text
                         ┌────────────────────┐
                         │       User         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │     Streamlit UI         │
                     └─────────┬────────────────┘
                               │
                               ▼
                    ┌───────────────────────────┐
                    │      Python Backend       │
                    └─────────┬─────────────────┘
                              │
     ┌────────────────────────┼─────────────────────────┐
     │                        │                         │
     ▼                        ▼                         ▼
┌──────────┐           ┌────────────┐          ┌────────────────┐
│ yt-dlp   │──────────▶│ Whisper AI │─────────▶│ Transcript Text │
└──────────┘           └────────────┘          └────────────────┘
                                                     │
                                                     ▼
                                       ┌────────────────────────┐
                                       │ HuggingFace Embeddings │
                                       └──────────┬─────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │  ChromaDB    │
                                          │ Vector Store │
                                          └──────┬───────┘
                                                 │
                                ┌────────────────┴────────────────┐
                                ▼                                 ▼
                      ┌────────────────┐                 ┌──────────────────┐
                      │ LangChain RAG  │───────────────▶│    Mistral AI     │
                      └────────────────┘                 └──────────────────┘
                                                             │
             ┌───────────────────────────────────────────────┼─────────────────────────────────────┐
             ▼                                               ▼                                     ▼
     Meeting Summary                               Action Items                          Chat with Meeting
             │                                               │
             └──────────────────────────────┬────────────────┘
                                            ▼
                                  Professional PDF Report
                                       (ReportLab)
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core backend development |
| **Streamlit** | Interactive web application |
| **OpenAI Whisper** | Speech-to-text transcription |
| **LangChain** | RAG pipeline orchestration |
| **Mistral AI** | LLM for summarization & question answering |
| **ChromaDB** | Vector database |
| **HuggingFace Embeddings** | Semantic embeddings |
| **yt-dlp** | Download audio from YouTube |
| **ReportLab** | PDF report generation |

---

# ⚙️ Workflow

1. User enters a YouTube URL.
2. yt-dlp downloads the audio.
3. Whisper converts speech into text.
4. Transcript is split into semantic chunks.
5. HuggingFace Embeddings generate vector representations.
6. ChromaDB stores transcript embeddings.
7. LangChain retrieves relevant chunks.
8. Mistral AI generates:
   - Meeting Title
   - Summary
   - Action Items
   - Key Decisions
   - Open Questions
9. Users can interact with the meeting using AI-powered RAG chat.
10. ReportLab exports the final meeting report as a PDF.

---

# 📊 AI Capabilities

- Speech-to-Text
- Meeting Summarization
- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Intelligent Question Answering
- Knowledge Extraction
- PDF Report Generation

---

# 📸 Screenshots

### Dashboard

_Add dashboard screenshot here_

### Meeting Summary

_Add summary screenshot here_

### AI Chat

_Add RAG chat screenshot here_

### PDF Export

_Add export screenshot here_

---

# 🚀 Installation

```bash
git clone https://github.com/Naincy33/MeetMind-AI.git

cd MeetMind-AI

pip install -r requirements.txt

streamlit run app.py
```

---

# 📂 Project Structure

```
MeetMind-AI/
│
├── app.py
├── main.py
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   ├── vector_store.py
│   └── diarization.py
│
├── utils/
│   ├── audio_processor.py
│   └── pdf_generator.py
│
├── downloads/
├── vector_db/
├── requirements.txt
└── README.md
```

---

# 🎯 Future Enhancements

- Speaker Diarization
- Meeting History
- Multi-document RAG
- Speaker Analytics
- Keyword Timeline
- Cloud Storage Integration
- Live Meeting Support
- Multi-language Transcription

---

# 👩‍💻 Developer

**Naincy**

B.Tech CSE Student | AI & ML Enthusiast

- GitHub: https://github.com/Naincy33
- LinkedIn: www.linkedin.com/in/naincy33

---

## ⭐ If you found this project useful, consider giving it a star!