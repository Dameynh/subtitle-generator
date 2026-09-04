# SEE INSTRUCTIONS BELOW

# IMPORTS, WHISPER, GRANITE

import os
from faster_whisper import WhisperModel
model = WhisperModel("large-v3",device="cpu",compute_type="int8")
from llama_cpp import Llama
llm = Llama.from_pretrained(
    repo_id="ibm-granite/granite-3.3-8b-instruct-GGUF",
    filename="granite-3.3-8b-instruct-Q4_K_M.gguf",
    n_ctx=4096
)

print("Granite 3.3 loaded successfully!")


# F U N C T I O N S


def convert_time(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = round((total_seconds - int(total_seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def transcribe_video(segments):
    subtitle_segments = []
    for segment in segments:
        start = segment.start
        end = segment.end
        text = segment.text
        subtitle_segments.append((start, end, text.strip()))
    return subtitle_segments


def create_original_srt(subtitle_segments2):
    subtitle_entries = []
    for number, (start, end, text) in enumerate(subtitle_segments2, start=1):
        start = convert_time(start)
        end = convert_time(end)
        subtitle_entry = f"{number}\n{start} --> {end}\n{text}"
        subtitle_entries.append(subtitle_entry)
    srt_content = "\n\n".join(subtitle_entries)
    return srt_content


# T R A N S L A T O R     F U N C T I O N

def translator(previous_text, current_text, next_text):
    system_prompt = """
    You are a professional subtitle translator specializing
    in natural spoken dialogue.

    Your ONLY task is to translate the CURRENT subtitle into natural,
    accurate English.

    The CURRENT subtitle may be written in ANY language.

    The PREVIOUS and NEXT subtitles are provided ONLY as context to help you
    understand the CURRENT subtitle. They must never be translated, copied,
    combined with CURRENT, or included in your response.

    IMPORTANT — MEANING OVER LITERAL WORDING:

    Translate what the speaker actually means, not simply the literal words.

    For idioms, fixed expressions, slang, cultural expressions, and figurative
    language, understand their meaning in context and express that meaning
    naturally in English.

    Do NOT translate an idiom literally when its figurative meaning is clear.

    For ordinary, non-idiomatic sentences, translate them faithfully and naturally.

    If the source language appears unusual, incomplete, ambiguous, or contains
    a possible transcription error, use the PREVIOUS and NEXT context to
    determine the most plausible intended meaning. Do not invent unrelated
    information.

    Preserve:
    - the original meaning and intent
    - tone and emotion
    - natural spoken English
    - appropriate level of formality
    - concise subtitle wording

    CRITICAL CONTEXT RULES:

    - Translate ONLY CURRENT.
    - PREVIOUS and NEXT are context, NOT additional text to translate.
    - Do NOT copy any sentence or phrase from PREVIOUS.
    - Do NOT copy any sentence or phrase from NEXT.
    - Do NOT combine CURRENT with PREVIOUS or NEXT.
    - Do NOT continue CURRENT using words from PREVIOUS or NEXT.
    - Even if CURRENT and NEXT are similar, repetitive, or closely related,
      translate CURRENT independently.
    - Even if PREVIOUS and NEXT appear to form a continuation of CURRENT,
      output only the translation of CURRENT.
    - The output must correspond semantically to CURRENT alone.
    - If CURRENT is already English, return it unchanged.

    STRICT OUTPUT RULES:

    Translate ONLY the CURRENT subtitle.

    Your response must contain ONLY the final English translation.

    Do NOT:
    - translate PREVIOUS or NEXT
    - include PREVIOUS or NEXT in your response
    - explain your translation
    - provide reasoning
    - provide notes
    - provide alternatives
    - analyze the source text
    - repeat the source text
    - add labels
    - add headings
    - add quotation marks around the translation
    - add commentary before or after the translation

    NEVER output labels such as:
    "Previous subtitle:"
    "Current subtitle:"
    "Next subtitle:"
    "Translation:"
    "English:"

    Do not output XML tags, section names, or any part of the prompt.

    The first character of your response must be the beginning of the English
    translation itself.

    The output will be inserted directly into an SRT subtitle file.
    Anything other than the final English translation will corrupt the subtitle.

    OUTPUT ONLY THE FINAL ENGLISH TRANSLATION OF CURRENT.
    """

    prompt = f"""
    You must translate ONLY the text inside <CURRENT>.

    <PREVIOUS>
    {previous_text}
    </PREVIOUS>

    <CURRENT>
    {current_text}
    </CURRENT>

    <NEXT>
    {next_text}
    </NEXT>
    """

    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=100,
        temperature=0
    )
    return output["choices"][0]["message"]["content"].strip()



def translate_original_srt_en(subtitle_segments2):
    translated_entries = []
    for i, (start, end, text) in enumerate(subtitle_segments2):


        if i > 0:
            previous_text = subtitle_segments2[i - 1][2]
        else:
            previous_text = ""


        if i < len(subtitle_segments2) - 1:
            next_text = subtitle_segments2[i + 1][2]
        else:
            next_text = ""


        current_text = text


        translated_text = translator(
            previous_text,
            current_text,
            next_text
        )

        start = convert_time(start)
        end = convert_time(end)

        number = i + 1

        subtitle_entry = f"{number}\n{start} --> {end}\n{translated_text}"

        translated_entries.append(subtitle_entry)

    translated_srt_content = "\n\n".join(translated_entries)
    return translated_srt_content




#-----------------------------------------------------------------------------------------------------------------------
# M A I N   P R O G R A M
# ============================================================
# USER: ENTER YOUR VIDEO FOLDER PATH (with reference to the code below)
# ============================================================
#
# The user must enter ONLY the path to the folder containing
# the MP4 files.
#
# IMPORTANT:
#     video_folder = FOLDER PATH ONLY
#
# Do NOT include the name of an MP4 file in video_folder.
#
# macOS example:
#     /Users/YourName/Movies/MyVideos
#
# Windows example:
#     C:\Users\YourName\Videos\MyVideos
#
# Do NOT enter:
#     /Users/YourName/Movies/MyVideos/episode01.mp4
#
# The program automatically finds the MP4 filenames inside
# the folder and creates the complete path to each video.
#
#
# HOW THE PATH HANDLING WORKS:
#
# User
#   ↓
# enters the folder path
#   ↓
# video_folder
#   ↓
# os.listdir(video_folder)
#   ↓
# gets the filenames inside that folder
#   ↓
# video_files
#   ↓
# the for loop takes one filename at a time
#   ↓
# video_file
#   ↓
# os.path.join(video_folder, video_file)
#   ↓
# combines the folder path + current filename
#   ↓
# current_path
#   ↓
# complete path to the MP4 currently being processed
#
#
# Example:
#
# User enters:
#     video_folder = /Users/YourName/Movies/MyVideos
#
# The folder contains:
#     episode01.mp4
#     episode02.mp4
#     episode03.mp4
#
# os.listdir(video_folder)
#     → finds the filenames inside the folder.
#
# video_files
#     → stores the MP4 filenames:
#        ["episode01.mp4", "episode02.mp4", "episode03.mp4"]
#
# for video_file in video_files:
#     → the loop processes each filename one at a time.
#
# os.path.join(video_folder, video_file)
#     → joins the folder path with the current filename.
#
# If video_file is:
#     episode01.mp4
#
# current_path becomes:
#     /Users/YourName/Movies/MyVideos/episode01.mp4
#
# The next loop iteration creates the path for episode02.mp4,
# then episode03.mp4, and so on.
#
# In short:
#
# User → gives folder
#      → os.listdir() gets filenames
#      → video_files stores the filenames
#      → for loop picks each filename
#      → os.path.join() combines folder + filename
#      → current_path becomes the complete video path
#
# Therefore:
#  The user only needs to enter the PATH TO THE FOLDER containing the MP4 files.
#     video_folder = folder path ONLY
#     video_file   = MP4 filename ONLY (filename found automatically by the program)
#     current_path = complete path INCLUDING the MP4 filename created automatically.
#
# ============================================================

while True:
    video_folder = input("Enter the path to your folder containing MP4 files: ").strip()

    if os.path.isdir(video_folder):
        break

    print("Invalid folder path. Please enter a valid folder path.")

video_files = []

for file in os.listdir(video_folder):
    if file.lower().endswith(".mp4"):
        video_files.append(file)
if not video_files:
    print("No MP4 files found in the selected folder.")
    exit()
while True:
    for video_file in video_files:
        current_path = os.path.join(video_folder, video_file)
        srt_path = os.path.splitext(current_path)[0] + ".srt"
        while True:
            subtitles_needed = input(f"Do you need subtitles for this mp4 file? {video_file} (y/n): ").lower()
            if subtitles_needed == "y":
                if os.path.exists(srt_path):
                    while True:
                        regenerate = input("Do you want to regenerate subtitles for this mp4 file since they already exist? (y/n): ").lower()
                        if regenerate == "y":
                            while True:
                                audio_lang = input("Audio language (Auto/Manual): ").capitalize()
                                if audio_lang == "Manual":
                                    while True:
                                        language = input("Enter the audio language code (e.g. de, en, fr): ").lower()
                                        if language in model.supported_languages:
                                            segments, info = model.transcribe(current_path, language=language)
                                            break
                                        else:
                                            print("Invalid language code. Please try again.")
                                    break
                                elif audio_lang == "Auto":
                                    segments, info = model.transcribe(current_path)
                                    break
                                else:
                                    print("Please enter manual or auto")
                            while True:
                                subtitle_lang = input("Subtitle language (Same/English): ").capitalize()
                                if subtitle_lang == "Same":
                                    subtitle_segments2 = transcribe_video(segments)
                                    original_srt = create_original_srt(subtitle_segments2)
                                    with open(srt_path, "w") as file:
                                        file.write(original_srt)
                                    break
                                elif subtitle_lang == "English":
                                    subtitle_segments2 = transcribe_video(segments)
                                    translated_content = translate_original_srt_en(subtitle_segments2)
                                    with open(srt_path, "w") as file:
                                        file.write(translated_content)
                                    break
                                else:
                                    print("Please enter Same or English")
                            break
                        elif regenerate == "n":
                            break
                        else:
                            print("Please enter either 'y' or 'n': ")
                    break
                else:
                    while True:
                        audio_lang = input("Audio language (Auto/Manual): ").capitalize()
                        if audio_lang == "Manual":
                            while True:
                                language = input("Enter the audio language code (e.g. de, en, fr): ").lower()
                                if language in model.supported_languages:
                                    segments, info = model.transcribe(current_path, language=language)
                                    break
                                else:
                                    print("Invalid language code. Please try again.")
                            break
                        elif audio_lang == "Auto":
                            segments, info = model.transcribe(current_path)
                            break
                        else:
                            print("Please enter manual or auto")
                    while True:
                        subtitle_lang = input("Subtitle language (Same/English): ").capitalize()
                        if subtitle_lang == "Same":
                            subtitle_segments2 = transcribe_video(segments)
                            original_srt = create_original_srt(subtitle_segments2)
                            with open(srt_path, "w") as file:
                                file.write(original_srt)
                            break
                        elif subtitle_lang == "English":
                            subtitle_segments2 = transcribe_video(segments)
                            translated_content = translate_original_srt_en(subtitle_segments2)
                            with open(srt_path, "w") as file:
                                file.write(translated_content)
                            break
                        else:
                            print("Please enter Same or English")
                    break
            elif subtitles_needed == "n":
                break
            else:
                print("Please enter either 'y' or 'n': ")
    print("All mp4 files scanned")
    while True:
        restart = input("Do you wish to restart? (y/n): ").lower()
        if restart == "y":
            break
        elif restart == "n":
            print("BYE!")
            exit()
        else:
            print("Please enter either 'y' or 'n': ")






# ============================================================
# INSTALLATION & SETUP NOTES
# WHISPER + GRANITE 3.3 8B INSTRUCT
# ============================================================
#
# This is the completed local version of the subtitle project.
#
# Pipeline:
#
#     MP4 video
#          ↓
#     Faster-Whisper / Whisper large-v3
#          ↓
#      transcription
#          ↓
#     SRT subtitle file
#          ↓
#     Granite 3.3 8B Instruct
#          ↓
#     English translation
#          ↓
#     English SRT subtitle file
#
#
# ============================================================
# 1. PRACTICALITIES
# ============================================================
#
# This project uses:
#     faster-whisper
#     llama-cpp-python
#     Granite 3.3 8B Instruct
#     Python 3 (PyCharm)
#
# ============================================================
# 2. INSTALL FASTER-WHISPER
# ============================================================
#
# Open PyCharm's built-in Terminal and install:
#
#     pip install faster-whisper
#
# Faster-Whisper is the Whisper implementation used by this
# project.
#
# The program uses the Whisper large-v3 model.
#
# The Whisper model does NOT need to be manually downloaded.
# Faster-Whisper downloads the required model automatically
# when it is first loaded by the program.
#
# Therefore, an Internet connection is required on the first
# run when the Whisper model is not already present locally.
#
#
# ============================================================
# 3. INSTALL LLAMA-CPP-PYTHON
# ============================================================
#
# In the same PyCharm Terminal, install:
#
#     pip install llama-cpp-python
#
# This package allows the program to run the Granite GGUF
# language model locally.
#
# No Ollama installation is required.
#
#
# ============================================================
# 4. GRANITE 3.3 8B INSTRUCT (Approx 5-6 GB)
# ============================================================
#
# This project uses:
#
#     IBM Granite 3.3 8B Instruct
#
# GGUF model:
#
#     granite-3.3-8b-instruct-Q4_K_M.gguf
#
# Hugging Face repository:
#
#     ibm-granite/granite-3.3-8b-instruct-GGUF
#
# Official repository:
#
#     https://huggingface.co/ibm-granite/granite-3.3-8b-instruct-GGUF
#
#
# ============================================================
# 5. GRANITE MODEL DOWNLOAD
# ============================================================
#
# The Granite GGUF file does NOT need to be manually downloaded
# or placed into a models folder.
#
# The program downloads it automatically using:
#
#     Llama.from_pretrained()
#
# The relevant code is:
#
#     from llama_cpp import Llama
#
#     llm = Llama.from_pretrained(
#         repo_id="ibm-granite/granite-3.3-8b-instruct-GGUF",
#         filename="granite-3.3-8b-instruct-Q4_K_M.gguf",
#         n_ctx=4096
#     )
#
# On the first run, llama-cpp-python downloads the specified
# Granite model from Hugging Face and stores it in the local
# Hugging Face cache.
#
# Subsequent runs can use the locally cached model without
# downloading it again, provided the cache has not been deleted.
#
#

#
# ============================================================
# 6. SUBTITLE FILE NAMING
# ============================================================
#
# The generated subtitle file uses the same base filename
# as the video:
# For example:
#     S1 E1 (ABC).mp4
#     S1 E1 (ABC).srt (new generated)
#
# The program does not require the MP4 to have a specific
# filename. Any .mp4 filename can be processed.
#
#
# ============================================================
# 7. LOCAL PROCESSING
# ============================================================
#
# Both Whisper and Granite run locally on the computer.
#
# Whisper:
#
#     Audio → detected/specified language transcription
#
# Granite:
#
#      English translation of subtitles
#
# No translation API or external translation server is used
# by this version.
#
#
# ============================================================
# 8. INFO on GRANITE AND WHISPER
# ============================================================

# Whisper large-v3 produced satisfactory transcriptions
# for the source videos.
#
# Multiple local translation models were tested (see below) before selecting
# IBM Granite 3.3 8B Instruct for this version.

# The Whisper transcription and SRT architecture can remain
# largely unchanged when replacing the translator.

# Key translation model selection criteria included:
# - translation quality
# - multilingual capability
# - local/offline operation
# - no API costs or rate limits
# - practical model size and performance
# - permissive licensing
#
# Granite 3.3 8B Instruct is released under the Apache 2.0 license.
#
# Official sources:
# Hugging Face:
# https://huggingface.co/ibm-granite/granite-3.3-8b-instruct
#
# IBM Granite GitHub:
# https://github.com/ibm-granite/granite-3.3-language-models
#
# IBM Granite official website:
# https://www.ibm.com/granite

# ============================================================
# Notes on other models which were tested
# ============================================================

# Multiple local translation models were evaluated during development
# before selecting IBM Granite 3.3 8B Instruct for this version.

# Models evaluated during development:
# OPUS-MT → Evaluated; not selected for this project based on our testing.
# Granite 4.1 8B → Evaluated; results were broadly at par with Granite 3.3 in our testing.
# LibreTranslate/Argos → Evaluated; not selected based on our testing and setup experience.
# MADLAD-400 → Evaluated; not selected based on the tested configuration and our project requirements.
# NLLB-200 → Evaluated; not selected based on our testing and project requirements.
# Phi-4-mini-instruct → Evaluated; not selected based on our testing and project requirements.
# GPT-OSS 20B → Evaluated; not selected based on our testing and project requirements.


