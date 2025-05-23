<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white"/>
  <img src="https://img.shields.io/badge/SpeechRecognition-FFB400?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/PyAudio-4A4A4A?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/ElevenLabs-AE00FF?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Pygame-0BDA51?style=for-the-badge&logo=pygame&logoColor=white"/>
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white"/>
  <img src="https://img.shields.io/badge/MIT-License-green?style=for-the-badge"/>
</p>

---

<h1 align="center">✨ Aurix AI Desktop Assistant</h1>
<p align="center"><i>Your smart, AI-powered personal assistant for desktop automation and interaction</i></p>

---

## 📌 Overview

> Aurix is a **voice-enabled AI assistant** for your desktop. It listens, understands, and acts — using natural language commands. Whether you want to **launch apps, control system settings, search the web**, or hear responses in a natural voice — Aurix has you covered.

---

## 🧠 Core Features

| Category             | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| 🎙 Voice Recognition | Understands voice commands with SpeechRecognition + PyAudio                 |
| 🗣 Text-to-Speech     | Replies via ElevenLabs or pyttsx3                                           |
| 🖥 GUI Interface       | Interactive desktop app built with PyQt5                                   |
| 📂 App Launcher       | Opens applications and files using custom commands                         |
| 💻 System Controls    | Adjusts system volume and brightness using pycaw & screen_brightness_control |
| 🌐 Web Integration    | Fetches search results and answers using Google + BeautifulSoup            |
| ⚙ Configuration       | YAML-based config for custom settings and preferences                      |

---

## 🧩 Tech Stack

| Tool/Library            | Description                                       |
|--------------------------|---------------------------------------------------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat) | Programming Language |
| ![PyQt5](https://img.shields.io/badge/-PyQt5-41CD52?logo=qt&style=flat) | GUI Development |
| ![SpeechRecognition](https://img.shields.io/badge/-SpeechRecognition-FFB400?style=flat) | Voice Input |
| ![PyAudio](https://img.shields.io/badge/-PyAudio-4A4A4A?style=flat) | Microphone Input |
| ![ElevenLabs](https://img.shields.io/badge/-ElevenLabs-AE00FF?style=flat) | Natural Voice API |
| ![Pyttsx3](https://img.shields.io/badge/-pyttsx3-FF69B4?style=flat) | Offline TTS |
| ![PyCaw](https://img.shields.io/badge/-PyCaw-FF6347?style=flat) | Volume Control |
| ![Pygame](https://img.shields.io/badge/-Pygame-0BDA51?style=flat) | Multimedia & Audio |
| ![BeautifulSoup](https://img.shields.io/badge/-BeautifulSoup-8A2BE2?style=flat) | HTML Parsing |
| ![Requests](https://img.shields.io/badge/-Requests-0066A1?style=flat) | HTTP Client |
| ![dotenv](https://img.shields.io/badge/-Dotenv-3C3C3C?style=flat) | API Key Management |
| ![YAML](https://img.shields.io/badge/-YAML-cccc00?style=flat) | Configuration |
| ![Windows](https://img.shields.io/badge/-Windows-0078D6?logo=windows&style=flat) | Supported OS |

---

## ⚙️ Installation Guide

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/Yogiii13/Aurix-ai-desktop-assistant.git
cd aurix-ai-desktop-assistant
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
# Activate
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Environment Variables

Create a `.env` file with your keys:

```env
ELEVEN_LABS_API_KEY=your_api_key_here
```

### 5️⃣ Launch Aurix

```bash
python main.py
```

---

## 🧪 Configuration

Aurix uses a `config.yaml` file to customize behavior:

```yaml
voice:
  engine: elevenlabs
  language: en
commands:
  open_browser: "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

🎯 Customize:
- Default voice
- App paths
- Trigger phrases
- Responses

---

## 💡 How to Use

🎤 **Voice Mode**  
Speak directly to Aurix after launching. Use commands like:

- "Open Chrome"
- "What's the weather?"
- "Reduce brightness"
- "Search Python tutorials"

💻 **Text Mode**  
Type your commands directly if preferred.

📊 **GUI Mode vs Headless**  
Use the GUI for ease of interaction or run in headless CLI mode.

---

## 🙌 Contributing

We ❤️ contributors! Here's how you can help:

1. Fork this repo
2. Create a branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -am 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a pull request

---

## 📄 License

Aurix is released under the [MIT License](LICENSE).  
Feel free to use, modify, and share it!

---

> ✨ *Built with love for automation and AI enthusiasts.*
