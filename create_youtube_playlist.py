import json
import os
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# ----------- CONFIG -----------
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
PLAYLIST_FILE = "playlist.json"
CACHE_FILE = "added_videos.json"
PLAYLIST_ID_FILE = "playlist_id.txt"
# ------------------------------

def try_add_video(youtube, playlist_id, video_id, title, retries=3):
    for attempt in range(retries):
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            print(f"✅ Added: {title}")
            return True
        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 409 and attempt < retries - 1:
                print(f"⚠️ 409 error on '{title}' — retrying in 3s...")
                time.sleep(3)
            else:
                print(f"❌ Failed to add '{title}': {e}")
                return False

def authenticate_youtube():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def create_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    print(f"🎉 Playlist created: https://www.youtube.com/playlist?list={response['id']}")
    return response["id"]

def search_and_add_videos(youtube, playlist_id, videos, added_video_ids):
    for video in videos:
        print(f"\n🔎 Searching: {video['query']}")

        search_results = youtube.search().list(
            part="snippet",
            q=video["query"],
            type="video",
            maxResults=video.get("max_results", 1)
        ).execute()

        for item in search_results["items"]:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]

            if video_id not in added_video_ids:
                if try_add_video(youtube, playlist_id, video_id, title):
                    added_video_ids.add(video_id)
            else:
                print(f"⏩ Skipped duplicate (seen before): {title}")

def main():
    # Load playlist JSON
    with open(PLAYLIST_FILE, "r") as f:
        data = json.load(f)

    # Load cache of added video IDs
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            added_video_ids = set(json.load(f))
    else:
        added_video_ids = set()

    # Authenticate and get playlist
    youtube = authenticate_youtube()

    if os.path.exists(PLAYLIST_ID_FILE):
        with open(PLAYLIST_ID_FILE, "r") as f:
            playlist_id = f.read().strip()
        print(f"📂 Reusing existing playlist: https://www.youtube.com/playlist?list={playlist_id}")
    else:
        playlist_id = create_playlist(youtube, data["title"], data["description"])
        with open(PLAYLIST_ID_FILE, "w") as f:
            f.write(playlist_id)

    # Add videos to playlist
    search_and_add_videos(youtube, playlist_id, data["videos"], added_video_ids)

    # Save updated video ID cache
    with open(CACHE_FILE, "w") as f:
        json.dump(list(added_video_ids), f, indent=2)

if __name__ == "__main__":
    main()