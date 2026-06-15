# MindEase  CBT-Based AI Mental Health Chatbot

> *Your safe space to heal & grow* 💜

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace%20Spaces-blue)](https://huggingface.co/spaces/foziakahn/MindEase-Mental-Health)
[![Python](https://img.shields.io/badge/Python-3.10-green)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Deployed-blue)](https://docker.com)

---

## Overview

MindEase is an AI-powered mental health chatbot built with CBT (Cognitive Behavioral Therapy) principles. It detects emotions in real time, responds with warmth and empathy, supports both English and Urdu, and immediately escalates to crisis helplines when needed.

Most mental health chatbots feel scripted. MindEase was built to feel human.

---

## Live Demo

🔗 [https://huggingface.co/spaces/foziakahn/MindEase-Mental-Health](https://huggingface.co/spaces/foziakahn/MindEase-Mental-Health)

---

## Features

- 🧠 **Real-Time Emotion Detection** → Detects 6 emotional states: sadness, anxiety, anger, guilt, neutral, and crisis using a hybrid keyword + ML approach
- 🚨 **Crisis Detection System** → Instantly detects self-harm and suicidal language and responds with Umang Pakistan helpline (0317-4288665)
- 🌍 **Multilingual Support** → Automatically detects and replies in English, Urdu, or Roman Urdu
- 💬 **CBT-Based Responses** → Every reply is grounded in Cognitive Behavioral Therapy techniques including thought reframing, validation, and behavioral activation
- ⚡ **LLM Fallback Chain** → Tries multiple free OpenRouter models in sequence to ensure response availability
- 🐳 **Dockerized Deployment** → Containerized and deployed on Hugging Face Spaces with always-on hosting

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Emotion Detection | Hugging Face Transformers — `j-hartmann/emotion-english-distilroberta-base` |
| LLM API | OpenRouter (GPT, Mistral, Gemma via free tier) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Deployment | Docker, Hugging Face Spaces |
| Environment | python-dotenv |

---

## System Architecture

```
User Message
     │
     ▼
Crisis Keyword Check ──► Crisis Detected → Return Helpline Response
     │
     ▼
Emotion Detection
  ├── Step 1: Keyword Matching (priority-based, covers Roman Urdu)
  └── Step 2: ML Fallback — DistilRoBERTa (confidence > 0.75)
     │
     ▼
Language Detection (English / Urdu / Roman Urdu)
     │
     ▼
LLM Call via OpenRouter (Fallback Chain: GPT → Mistral → Gemma)
     │
     ▼
Response Trimmed to 2 Sentences
     │
     ▼
Return Reply + Detected Emotion to Frontend
```

---

## Emotion Detection Algorithm

The system uses a **hybrid two-step approach**:

**Step 1  Keyword Matching (Primary)**
- Priority-ordered dictionary covers 6 emotion categories
- Handles Roman Urdu phrases like `udaas`, `ghabra`, `gussa`, `pareshan`
- Multi-word phrase matching + regex word boundary detection
- Neutral greetings are caught first to prevent false positives

**Step 2  ML Model (Fallback)**
- Model: `j-hartmann/emotion-english-distilroberta-base`
- Only trusted when confidence score > 0.75
- Maps `fear → anxiety` and `disgust → anger`
- Falls back to `neutral` if confidence is low

---

## Crisis Detection

Crisis detection runs **before** emotion detection as the highest priority layer.

Triggers on keywords including:
- English: `kill myself`, `want to die`, `hurt myself`, `end my life`
- Roman Urdu: `marna chahta`, `jeena nahi chahta`, `zindagi khatam`

Immediate response includes **Umang Pakistan helpline: 0317-4288665** (24/7).

---

## Project Structure

```
MindEase-AI-Mental-Health/
│
├── app.py                  # Flask backend, routes, emotion logic, LLM calls
├── requirements.txt        # Python dependencies
├── .gitignore              # Excludes .env and sensitive files
│
└── templates/
    ├── index.html          # Landing page with chat preview
    └── chat.html           # Full chat interface
```

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/Iamfouzia/MindEase-AI-Mental-Health.git
cd MindEase-AI-Mental-Health

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
echo "MISTRAL_API_KEY=your_openrouter_api_key_here" > .env

# 4. Run the app
python app.py
```

App will be running at `http://localhost:5000`

---

## CBT Techniques Used

| Technique | Implementation |
|---|---|
| Thought Reframing | Prompted into every LLM response |
| Emotional Validation | Always acknowledge emotion before advice |
| Behavioural Activation | Suggested for sadness and low mood states |
| Breathing Techniques | Triggered for anxiety detection |
| Journaling | Suggested as a long-term coping tool |

---

## Deployment

The app is containerized using **Docker** and deployed on **Hugging Face Spaces** for always-on hosting.

```dockerfile
# Hugging Face Spaces auto-detects Docker deployment
# No manual server management required
```

---

## What This Project Taught Me

→ Prompt engineering is a real skill. Making AI feel human takes 100 iterations, not 10.

→ The best projects are built for people, not portfolios.

→ Getting the tone right for crisis detection is the hardest part one wrong response can break trust completely.

→ CBT principles translate surprisingly well into prompt structure.

## Author

**Fouzia Khan**

[GitHub](https://github.com/Iamfouzia) · [LinkedIn](https://linkedin.com/in/fouzia-khan-35a73a258)



## Screenshots
<img width="1920" height="772" alt="cbt5" src="https://github.com/user-attachments/assets/29fa49c9-322c-4360-ad76-41e9fc9799ef" />
<img width="1920" height="765" alt="cbt2" src="https://github.com/user-attachments/assets/a4739e8d-283e-4d76-bf44-e96263ec6cd9" />
<img width="1896" height="742" alt="cbt3" src="https://github.com/user-attachments/assets/2e824e19-3a27-4f73-881d-36642e022ac1" />
<img width="1889" height="751" alt="cbt(1338)" src="https://github.com/user-attachments/assets/79fd93ee-2f3f-420d-8495-f128af5406ab" />
<img width="1910" height="741" alt="cbt" src="https://github.com/user-attachments/assets/dc46e588-bcb6-46e8-8502-d9fd5db88835" />
<img width="1920" height="762" alt="cbt22" src="https://github.com/user-attachments/assets/de64409e-40cc-4ca7-b3ec-a0048c583784" />


