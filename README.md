# VerbaFlow - Verbal Communication Skills Trainer

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![License](https://img.shields.io/badge/license-MIT-red)

## 📌 Overview
VerbaFlow is an AI-powered Verbal Communication Skills Trainer designed to help users improve their speaking abilities through interactive chat, voice processing, and structured training activities. The application integrates with **Groq API** for AI-based feedback and **VoiceRSS** for text-to-speech conversion.

With VerbaFlow, users can practice **impromptu speaking, storytelling, and conflict resolution**, receiving AI-driven feedback on their tone, clarity, and engagement. Additionally, the app allows users to submit voice recordings or text-based presentations for assessment, helping them refine their verbal skills effectively.

---
## 🚀 Features

### 🎤 Interactive Communication Modes
- **Chat Interface**: Users can engage in AI-powered conversations to practice verbal clarity and coherence.
- **Voice Interaction**: Speech-to-text processing allows users to receive real-time feedback on their speech.
- **Text-to-Speech (TTS)**: AI-generated responses can be converted into speech for an immersive learning experience.

### 📚 Skill Training Modules
- **Impromptu Speaking**: Users receive random topics and must respond on the spot.
- **Storytelling**: AI evaluates users' storytelling techniques, narrative flow, and vocabulary.
- **Conflict Resolution**: Simulated scenarios help users improve negotiation and communication skills.

### 📊 Presentation Assessments
- **Text-Based Assessments**: Users can submit written presentations for AI-generated feedback.
- **Voice-Based Assessments**: Users can record or upload speeches, which are transcribed and analyzed for improvement areas.

### 💾 Progress Tracking
- Stores user responses and AI feedback in a **SQLite database**.
- Allows users to track improvement over time.

### 🔒 Secure API Integration
- Uses **Groq API** for AI-powered language processing.
- Uses **VoiceRSS API** for text-to-speech conversion.
- Stores API keys securely using environment variables.

---
## 🛠️ Setup Instructions

### 1️⃣ Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- **Flask**
- **pip (Python package manager)**
- **SQLite (for database storage)**

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/msp99000/verbaflow.git
cd verbaflow
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file in the project root and add your API keys:
```
GROQ_API_KEY=your_groq_api_key
VOICERSS_API_KEY=your_voicerss_api_key
```

### 5️⃣ Initialize the Database
```bash
python database/db_setup.py
```

### 6️⃣ Run the Application
```bash
python app.py
or
flask run --debug
```
The app will start on **http://127.0.0.1:5000/**

---
## 📂 Project Structure
```
verbaflow/
│── app.py                      # Main Flask Application
│── config.py                    # Configuration (API Keys)
│── templates/
│   ├── index.html               # Homepage UI
│   ├── chat.html                # Chat-based training UI
│   ├── voice.html               # Voice interaction UI
│   ├── assessment.html          # Presentation Assessment UI
│── static/
│   ├── styles.css               # Custom CSS
│   ├── scripts.js               # Frontend JS (AJAX for API Calls)
│── modules/
│   ├── llm_wrapper.py           # LLM API Wrapper (Groq API)
│   ├── speech_processing.py     # Speech-to-Text & Text-to-Speech
│   ├── training_modules.py      # Skill Training Activities
│── database/
│   ├── db_setup.py              # SQLite Setup
│   ├── user_data.db             # Database file
│── requirements.txt             # Dependencies
│── README.md                    # Project Instructions
```

---
## 📜 API Usage

### 🔹 Chat with AI (POST /chat)
```json
{
  "message": "How can I improve my presentation skills?"
}
```
Response:
```json
{
  "response": "To improve your presentation skills, focus on clarity, confidence, and structured delivery. Avoid filler words and maintain eye contact."
}
```

### 🔹 Submit Voice Input (POST /voice)
Uploads a voice recording and returns AI feedback.

### 🔹 Get Training Module (POST /train)
```json
{
  "module": "impromptu",
  "response": "Teamwork is important because it allows people to share ideas."
}
```
Response:
```json
{
  "feedback": "Your response is clear, but try to provide a real-life example for better engagement."
}
```

### 🔹 Presentation Assessment (POST /assess)
```json
{
  "text": "My speech is about the impact of AI on society."
}
```
Response:
```json
{
  "feedback": "Great introduction! Try adding statistics to strengthen your argument."
}
```

---
## 🚀 Future Improvements
- **Multi-Language Support**: Expand AI feedback to support multiple languages.
- **Advanced Speech Analysis**: Evaluate tone, pace, and emotional expression.
- **AI-Based Personalized Training**: Adaptive learning plans based on user history.
- **Live Session Mode**: Real-time speech feedback with a virtual coach.

---
## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

---
## 📜 License
This project is licensed under the MIT License.

---
## 📩 Contact
For questions or suggestions, reach out at ✉️ [msp99000@gmail.com](mailto:msp99000@gmail.com).
