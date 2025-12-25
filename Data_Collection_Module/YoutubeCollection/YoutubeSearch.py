import os
import sys
import pandas as pd
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from dotenv import load_dotenv

load_dotenv()

# youtube client
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_SEARCH_API_KEY"))

script_dir = os.path.dirname(os.path.abspath(__file__))
comments_file = os.path.join(script_dir, "../../inputs-outputs/youtube_comments.csv")
transcripts_file = os.path.join(script_dir, "../../inputs-outputs/youtube_transcripts.csv")

# initial call to retrieve the videos
def find_videos(query):
    try:
        search_response = youtube.search().list(q=query, part="id,snippet", type="video", maxResults=20, order="relevance").execute()

        video_data = []
        video_ids = []

        # from doc
        for video in search_response.get("items"):
            video_id = video["id"]["videoId"]
            video_ids.append(video_id)
            video_data.append({"video_id": video_id, "title": video["snippet"]["title"], "channel": video["snippet"]["channelTitle"], "published_at": video["snippet"]["publishedAt"], "video_url": f"https://www.youtube.com/watch?v={video_id}"})
        
        return video_data, video_ids
    except Exception as e:
        print(f"Error retrieving YouTube videos: {e}")
        return [], []

# secondary calls to retrieve transcripts / comments for each video
def get_comments_transcipts(video_id, max_comments=100):
    transcript = None
    comments = []

    # changed from required transcript to optional, some videos disable transcripts (break prevention)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript])
    except TranscriptsDisabled:
        print(f"Transcript error from API, no transcript available.")
    except Exception as e:
        print(f"Error fetching transcript: {e}")

    # fetch comments
    try:
        next_page_token = None
        comments_fetched = 0

        # 100 comments per call
        while comments_fetched < max_comments:
            request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=min(100, max_comments - comments_fetched), textFormat="plainText", pageToken=next_page_token)
            response = request.execute()

            # from doc
            for item in response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comment_text = top_comment["textDisplay"]
                likes = top_comment["likeCount"]
                published_at = top_comment["publishedAt"]

                comments.append({"video_id": video_id, "comment": comment_text, "likes": likes, "published_at": published_at})

                comments_fetched += 1
                if comments_fetched >= max_comments:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(0.5)  # adjustable for API rate limits
    except Exception as e:
        print(f"Error fetching comments for video: {e}")

    return transcript, comments

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter a product name as a second argument.'")
        sys.exit(1)

    product_name = sys.argv[1] + " Review"
    videos, video_ids = find_videos(product_name)

    # fixed to fetch both in 1 call to preserve API calls
    all_transcripts = []
    all_comments = []
    
    for video in videos:
        transcript, comments = get_comments_transcipts(video["video_id"])
        
        if transcript:
            all_transcripts.append({"video_id": video["video_id"], "title": video["title"], "transcript": transcript})
        all_comments.extend(comments)

    df_comments = pd.DataFrame(all_comments)
    df_transcripts = pd.DataFrame(all_transcripts)

    df_comments.to_csv(comments_file, index=False)
    print("YouTube comments saved successfully.")
    df_transcripts.to_csv(transcripts_file, index=False)
    print("YouTube transcripts saved successfully.")
