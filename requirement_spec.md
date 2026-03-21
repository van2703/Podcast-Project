# 📋 Requirement Specification (SRS)
**Project Name:** BBC News AI Podcast Transformer

## 1. Project Goal
Create a simple, manual pipeline to download BBC news, write a short podcast script using AI, and convert it to audio. The final podcast is 3 minutes long.

## 2. Core Features
* **Module 1 (Data Fetcher):** Download the top 5 latest news from BBC RSS Feed and save them as `.txt` files in a local folder (`/data`).
* **Module 2 (AI Script Writer):** Read the `.txt` files and use Gemini AI to write a 400-word script in simple English.
* **Module 3 (AI Voice Generator):** Convert the text script into an `.mp3` audio file.
* **Module 4 (Web Player):** Play the `.mp3` file on a simple GitHub Pages website.

## 3. Constraints
* **No auto-schedule:** The script runs manually when the user wants to update the podcast.
* **Local processing:** All text files are saved locally to check for "Fake News" before generating audio.
* **Simple tools:** Do not use heavy frameworks. Keep the code lightweight.