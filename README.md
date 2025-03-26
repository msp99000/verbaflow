# 🎤 VerbaFlow - AI-Powered Speech Coach

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![License](https://img.shields.io/badge/license-MIT-red)

Transform your speaking skills with real-time AI feedback. Practice conversations, improve presentations, and track your progress.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Conversation Simulator** | Practice with AI personas (interviewer, debater, storyteller) |
| **Speech Analysis** | Get scores on Structure, Delivery, and Content |
| **Skill Modules** | Focused training for impromptu speaking, storytelling, and conflict resolution |
| **Progress Dashboard** | Visualize your improvement over time |

## 🛠️ Tech Stack

**Backend**:
→ Python 3.11
→ Flask
→ SQLite/PostgreSQL

**AI**:
→ Groq API (Llama 3-8b)
→ Custom prompt engineering

**Frontend**:
→ Bootstrap 5
→ Chart.js
→ Web Speech API

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Groq API key](https://console.groq.com) (free)

```bash
# Clone and setup
git clone https://github.com/yourusername/verbaflow.git
cd verbaflow
python -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')" > .env
echo "GROQ_API_KEY=your_key_here" >> .env

# Run
flask run
