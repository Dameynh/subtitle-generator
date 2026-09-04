# Subtitle Generator

A local Python-based subtitle generator that transcribes video audio and generates subtitle files in the original language or translates them into English.

# Features

* 🎙️ **Speech-to-text transcription** using Faster-Whisper (large-v3)
* 🌍 **English translation** using IBM Granite 3.3 8B Instruct
* 📝 Generates standard **.srt** subtitle files
* 🔤 Supports subtitles in the **original language** or **English**
* 🎧 Supports automatic language detection or manual language selection
* 💻 Runs the transcription and translation locally
* 📁 Processes MP4 files from a user-selected folder
* 🔄 Can regenerate existing subtitle files when required

# How It Works

**MP4 Video** → **Faster-Whisper** → **Transcription** → **SRT Subtitles**  
→ **Granite 3.3 8B Instruct** → **English Translation** → **English SRT**


The project uses surrounding subtitle context when translating into English to help the model understand the meaning and context of spoken dialogue.

# Models

**Transcription**

* Faster-Whisper
* Whisper large-v3

**Translation**

* IBM Granite 3.3 8B Instruct
* GGUF Q4_K_M model

Both models are run locally.

# Demo

### English Subtitles

The first demo shows the generated subtitles translated into English. (./Demo/subtitle_test_clip%20(EN%20sub).mp4)

### Hindi Subtitles

The second demo shows the generated subtitles in the original language. (./Demo/subtitle_test_clip%20(HI%20sub).mp4)


# Setup

The Python file contains the relevant setup notes and explains how the models are downloaded and used.

# Project Notes

This project was developed and tested with multiple local translation models before selecting Granite 3.3 8B Instruct for the final version.

The model evaluation notes and implementation details are documented directly in **subtitle_generator.py**.

# Credits

* The code for this project was written by me.
* This project uses third-party libraries and models, including Faster-Whisper and IBM Granite.
* These remain the property of their respective developers and are used under their respective licenses.
* No ownership of these third-party components is claimed.

