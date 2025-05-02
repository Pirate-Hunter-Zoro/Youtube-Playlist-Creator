import json
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Scopes and API info
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate_youtube():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", scopes)
    credentials = flow.run_console()
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
    return response["id"]

def search_and_add_videos(youtube, playlist_id, queries):
    for video in queries:
        request = youtube.search().list(
            part="snippet",
            q=video["query"],
            type="video",
            maxResults=1
        )
        search_response = request.execute()
        video_id = search_response["items"][0]["id"]["videoId"]

        add_request = youtube.playlistItems().insert(
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
        )
        add_request.execute()
        print(f"✅ Added: {video['title']}")

def main():
    with open("study_playlist.json", "r") as f:
        data = json.load(f)

    youtube = authenticate_youtube()
    playlist_id = create_playlist(youtube, data["title"], data["description"])
    search_and_add_videos(youtube, playlist_id, data["videos"])
    print(f"🎉 Playlist created: https://www.youtube.com/playlist?list={playlist_id}")

if __name__ == "__main__":
    main()
