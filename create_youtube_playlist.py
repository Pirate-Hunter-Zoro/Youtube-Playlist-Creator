import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery

# ----------- CONFIG -----------
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
PLAYLIST_FILE = "study_playlist.json"
CACHE_FILE = "added_videos.json"
# ------------------------------

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
                "privacyStatus": "private"
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
                added_video_ids.add(video_id)
                print(f"✅ Added: {title}")
            else:
                print(f"⏩ Skipped duplicate (seen before): {title}")

def main():
    # Load playlist JSON
    with open(PLAYLIST_FILE, "r") as f:
        data = json.load(f)

    # Load previously added video IDs
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            added_video_ids = set(json.load(f))
    else:
        added_video_ids = set()

    # Authenticate and create playlist
    youtube = authenticate_youtube()
    playlist_id = create_playlist(youtube, data["title"], data["description"])

    # Search & add videos
    search_and_add_videos(youtube, playlist_id, data["videos"], added_video_ids)

    # Save updated cache
    with open(CACHE_FILE, "w") as f:
        json.dump(list(added_video_ids), f, indent=2)

if __name__ == "__main__":
    main()
