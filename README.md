# YouTube Playlist Creator

🎶 Automatically build and populate YouTube playlists from a custom JSON file using the YouTube Data API.

## Features
- Reads a playlist JSON with search queries and metadata
- Creates the playlist and adds multiple results per query
- Easy to customize, extend, and automate

## Setup
1. Enable YouTube Data API v3 in Google Cloud
2. Download your `client_secret.json`
3. Run:
   ```bash
   pip install -r requirements.txt
   python create_playlist.py
