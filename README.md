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
## 🖼️ Demo Screenshot

<p align="center">
  <img src="https://user-images.githubusercontent.com/39839898/239741685-3f61f1ec-27e7-4c1f-94a4-4e2e1e7a6ba0.png" alt="Aurix AI Desktop Assistant Screenshot" width="700"/>
</p>

*Aurix in action: GUI with voice/text chat, system controls, and real-time responses.*

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

###  Clone the Repo

```bash
git clone https://github.com/Yogiii13/Aurix-ai-desktop-assistant.git
cd aurix-ai-desktop-assistant
```

###  Create a Virtual Environment

```bash
python -m venv venv
# Activate
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

###  Install Dependencies

```bash
pip install -r requirements.txt
```
## 🦙 Ollama Configuration (Local LLM)

Aurix supports running open-source language models locally using [Ollama](https://ollama.com/). This lets you run LLMs on your own machine for privacy, speed, and offline use.

### 1️⃣ Install Ollama

- Download Ollama from [ollama.com/download](https://ollama.com/download) and install it following instructions for your OS.

### 2️⃣ Pull a Supported Model

This project is tested with the following models:
- `gemma:1b`
- `tinyllama:1.1b`
- `deepseek-r1:1.5b`

You can use any model supported by Ollama. To pull a model, run (replace with desired model name):

```bash
ollama pull gemma:1b
ollama pull tinyllama:1.1b
ollama pull deepseek-r1:1.5b
```

Explore more models at [ollama.com/library](https://ollama.com/library).

### 3️⃣ Start Ollama

Ollama usually runs automatically after installation. If not, you can start it manually:

```bash
ollama serve
```

This starts the Ollama server at `http://localhost:11434`.

### 4️⃣ Configure Aurix to Use Ollama

You need to tell Aurix which model to use by updating your `config.yaml` and `.env` files.

#### Example `config.yaml` section

```yaml
llm:
  provider: ollama
  model: gemma:1b    # or tinyllama:1.1b, deepseek-r1:1.5b, etc.
  api_base: http://localhost:11434
```

#### Example `.env` entries

```
LLM_PROVIDER=ollama
LLM_MODEL=gemma:1b           # or tinyllama:1.1b, deepseek-r1:1.5b, etc.
LLM_API_BASE=http://localhost:11434
```

You can switch models anytime by:
- Pulling the new model with `ollama pull <model-name>`.
- Updating the `model` value in your `config.yaml` and `.env` files.

---

**Note:**  
- Make sure the model you specify in your config has been pulled with `ollama pull`.
- Ollama must be running before you launch Aurix.
- For more advanced Ollama settings, see [Ollama documentation](https://ollama.com/docs/).

###  Set Environment Variables

Create a `.env` file with your keys:

```env
ELEVEN_LABS_API_KEY=your_api_key_here
```

###  Launch Aurix

```bash
python main.py
```

---

## ⚙️ Technical Requirements

### 🧰 Core Libraries
- `PyQt5==5.15.11` – GUI toolkit  
- `pywin32==307` – Windows-specific APIs  
- `SpeechRecognition==3.10.0` – Voice recognition  
- `ollama==0.1.0` – Text-to-speech  
- `python-dotenv==1.0.0` – Environment management  
- `PyYAML==6.0.1` – YAML config parsing  
- `beautifulsoup4==4.10.0` – HTML parsing  
- `requests==2.26.0` – HTTP library  

### 💻 System Control
- `pycaw==20220416` – Audio control  
- `screen_brightness_control==0.14.1` – Adjust screen brightness  

### 🗣️ Voice Components
- `pyttsx3==2.98` – TTS engine  
- `PyAudio==0.2.14` – Audio input/output  
- `elevenlabs==0.2.26` – Realistic synthetic voices  
- `pygame==2.6.1` – Game engine support  

### 🔍 Utilities
- `numpy==1.24.3` – Numerical processing  
- `sip==6.11.0` – C++ access  
- `google-search-results==2.4.2` – Google search API  

### 🧩 Optional
- `webview==0.1.5` – Embedded browser view  
- `psutil==5.9.5` – Process/system monitoring  

---

## ⚙️ Configuration

Customize Aurix with the `config.yaml` file to define:
- AI model settings
- Voice preferences
- Trigger words and responses
- Application launch commands

---

## 💡 Usage Tips

- Launch with:
  ```bash
  python main.py
  ```
- Use voice or type in the GUI to give commands.
- Run in **headless mode** for a CLI experience or enable the GUI for richer interaction.

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
