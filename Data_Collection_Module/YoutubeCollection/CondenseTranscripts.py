import os
import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, '../../inputs-outputs/youtube_transcripts.csv')
output_file = os.path.join(script_dir, '../../inputs-outputs/condensed_transcripts.csv')

def clean_text(text):
    patterns = [
        r"(don't forget to like and subscribe)",
        r"(please subscribe.*?channel)",
        r"(sponsored by.*)",
        r"(thanks for watching)",
        r"(see you in the next one)",
        r"(link in the description)",
        r"(make sure to hit the bell icon)",
        r"(smash that like button)"
        r"\[\s*music\s*\]"
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE) # fixed some patterns not being applied
    return text

if __name__ == "__main__":
    try:
        df = pd.read_csv(input_file)
    except:
        print("Could not load input file.")
    
    short_transcripts = []

    for _, row in df.iterrows():
        vid = row["video_id"]
        transcript = row.get("transcript", "")
        cleaned = clean_text(str(transcript))
        tokens = word_tokenize(cleaned)
        short_transcript = ' '.join(tokens[:600])  # max 600 word for token restrictions
        short_transcripts.append({"video_id": vid, "text": short_transcript})

    output_csv = pd.DataFrame(short_transcripts)
    output_csv.to_csv(output_file, index=False)
    print("Transcripts shortened.")
