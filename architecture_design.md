# 🏗️ Architecture Design

## 1. System Workflow
This project uses a "Separation of Concerns" architecture. Each step is a separate Python file.

```mermaid
graph TD;
    A[BBC RSS Feed] -->|1. fetch_bbc.py| B(Local /data folder);
    B -->|2. generate_script.py| C{Gemini AI Model};
    C -->|Output| D[podcast_script.txt];
    D -->|3. text_to_voice.py| E((bbc_podcast.mp3));
    E -->|Git Push| F[GitHub Pages HTML];
```

## 2. Tech Stack
* **Data Ingestion:** Python `feedparser`
* **AI Engine:** Google Gemini SDK (`google-genai`)
* **TTS Engine:** Microsoft Edge TTS (`edge-tts`)
* **Frontend:** HTML/CSS
* **Hosting:** GitHub Pages

## 3. Folder Structure
- `/data/`: Stores raw news `.txt` files.
- `fetch_bbc.py`: Code to download news.
- `generate_script.py`: Code to call AI for scripting.
- `text_to_voice.py`: Code to make audio.
- `index.html`: The web interface.