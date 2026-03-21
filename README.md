# 🎙️ BBC News AI Podcast Transformer

## About the Project
This is a simple automated data pipeline project. It downloads the latest world news from BBC, uses AI to write a 3-minute podcast script, and turns the text into voice. 

You can listen to the result here: **(file:///D:/Workspace/Podcast/index.html)**

## Features
* **Data Fetching:** Automatically downloads real news from BBC RSS Feed.
* **AI Scripting:** Uses Gemini AI to summarize news into simple English.
* **Text-to-Speech:** Uses Microsoft Edge TTS to create a natural-sounding voice.
* **Web Player:** A simple static page to play the `.mp3` file.

## Tech Stack
* **Language:** Python
* **AI Model:** Google Gemini 2.5 Flash
* **Libraries:** `feedparser`, `google-genai`, `edge-tts`, `python-dotenv`
* **Deployment:** GitHub Pages

## How It Works (Architecture)
Here is the simple workflow of this project:

```mermaid
graph TD;
    A[BBC RSS Feed] -->|fetch_bbc.py| B(Local /data folder);
    B -->|generate_script.py| C{Gemini AI};
    C -->|Output| D[podcast_script.txt];
    D -->|text_to_voice.py| E((bbc_podcast.mp3));
    E -->|Git Push| F[GitHub Pages Web Player];