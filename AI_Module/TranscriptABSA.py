import os
import pandas as pd
import ast
import re
import json
import torch
from transformers import pipeline

# Simple script using facebook LLM for advanced zero-shot-classification
# Could of implemented ABSA logic from Google ABSA, but tried a different approach for this

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "../inputs-outputs/cleaned_youtube_transcripts.csv")
output_file = os.path.join(script_dir, "../inputs-outputs/processed_youtube_transcripts.csv")

model = "facebook/bart-large-mnli"
classifier = pipeline("zero-shot-classification", model=model, truncation=True, max_length=512)

def extract_sentiment(sentence, aspect):
    # tweaked prompts to be simple for clarity  
    labels = [f"positive about {aspect}", f"negative about {aspect}", f"neutral about {aspect}"]
    result = classifier(sentence, labels)

    best_label = result["labels"][0].lower()
    best_score = result["scores"][0]

    if "positive" in best_label:
        sentiment = "positive"
    elif "negative" in best_label:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return sentiment, best_score

if __name__ == "__main__":
    df = pd.read_csv(input_file)

    output_rows = []

    # loop and apply for each row
    for _, row in df.iterrows():
        video_id = row["video_id"]
        title = row["title"]
        sentence = str(row["sentence"])
        # fixed not processing lists with literal_eval
        aspects = ast.literal_eval(row["aspect_labels"])

        if not aspects:
            continue

        aspect_sentiments = {}
        for aspect in aspects:
            model_label, model_score = extract_sentiment(sentence, aspect)
            aspect_sentiments[aspect] = { "sentiment_label": model_label, "sentiment_score": model_score }

        aspect_sentiments_json = json.dumps(aspect_sentiments)

        output_rows.append({"video_id": video_id, "title": title, "sentence": sentence, "aspect_sentiments": aspect_sentiments_json})

    final_df = pd.DataFrame(output_rows)
    final_df.to_csv(output_file, index=False)
    print(f"Zero-shot classification successfully completed.")