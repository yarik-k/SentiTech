import os
import pandas as pd
import json
import re
import spacy
import torch
from transformers import pipeline
import emoji
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nlp = spacy.load("en_core_web_sm")
device = torch.device("mps") # offload to MPS, change to CUDA if on colab

# truncation true, fixed for overflowing
sarcasm_model = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-irony", truncation=True, padding=True, max_length=256, device=device)
emotion_model = pipeline("text-classification", model="cardiffnlp/bertweet-base-emotion", truncation=True, padding=True, max_length=512, device=device)

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "../../inputs-outputs/cleaned_youtube_comments.csv")
output_file = os.path.join(script_dir, "../../inputs-outputs/processed_youtube_comments.csv")

def run_sarcasm(text, sarcasm_model_pipeline):
    if not text:
        return False

    results = sarcasm_model_pipeline([text])

    if len(results) > 0:
        label = results[0]["label"].upper()
        score = float(results[0]["score"])
        # if "IRONY" label is first then weigh score
        if "IRONY" in label and score >= 0.99: # adjusted, this model returns high scores
            return True

    return False

# mapping model labels to actual emotions fixed
# this model returns "LABEL_0, LABEL_1, etc..." from docs   
def get_emotion_distribution(text, model):
    if not text:
        return None

    try:
        results = model([text], top_k=None) # top_k = none for all labels

        if not results:
             print(f"Error processing emotion for: {text}")
             return None

        distribution = results[0]
        distribution.sort(key=lambda x: x["score"], reverse=True)

        final_distribution = []
        for item in distribution:
            model_label = item['label']
            score = item['score']

            label_string = model_label.split('_')[-1]
            label_id = int(label_string)

            id_map = {0: "anger", 1: "joy", 2: "optimism", 3: "sadness"}
            string_label = id_map.get(label_id)

            if string_label is None:
                string_label = "unknown" # preventing breakages, fix for model outputs but may introduce bad results

            final_distribution.append({"label": string_label, "score": score})

        return final_distribution
    except Exception as e:
        print(f"Error while processing text with emotion model.")
        return None

def extract_tops(json_str, original_text="", sarcasm_model_pipeline=None):
    try:
        emotion_dict = json.loads(json_str)
    except Exception:
        return ("unknown", 0.0, "neutral") # default return for breakages

    # extracting top emotion and score
    items = sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)
    top_emotion, top_score = items[0][0], items[0][1]

    # added logic, if top 2 emotions are very close (10%) then resort to mixed
    if len(items) > 1:
        second_emotion, second_score = items[1]
        if abs(top_score - second_score) < 0.10:
            return ("mixed", round(top_score, 4), "mixed")

    sentiment_map = {"joy": "positive", "optimism": "positive", "sadness": "negative", "anger": "negative", "mixed": "mixed", "sarcasm": "negative"}
    final_sentiment = sentiment_map.get(top_emotion, "neutral") # neutral default fix

    # sarcasm section
    is_sarcastic = run_sarcasm(original_text, sarcasm_model_pipeline)
    if is_sarcastic:
        final_sentiment = "negative"
        top_emotion = "sarcasm"

    return (top_emotion, round(top_score, 4), final_sentiment)

# quick conversion into json for cell added for handling
def format_data(emotion_list):
    data = {}
    for item in emotion_list:
        if "label" in item and "score" in item:
            data[item["label"]] = round(item["score"], 4)
    return json.dumps(data)

if __name__ == "__main__":
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")

    print("Running emotion analysis on comments") # debug
    emotion_results = []
    for comment in df["cleaned_comment"]:
        emotion_distribution = get_emotion_distribution(comment, emotion_model)
        formatted = format_data(emotion_distribution)
        emotion_results.append(formatted)

    df["emotion_analysis"] = emotion_results

    top_emotions = []
    emotion_scores = []
    sentiments = []

    for i in range(len(df)):
        emotion_json = df.loc[i, "emotion_analysis"] # fixed cells not selecting
        original_text = df.loc[i, "cleaned_comment"]

        top_emotion, score, sentiment = extract_tops(emotion_json, original_text=original_text, sarcasm_model_pipeline=sarcasm_model)

        top_emotions.append(top_emotion)
        emotion_scores.append(score)
        sentiments.append(sentiment)

    # removed ABSA logic
    df["top_emotion"] = top_emotions
    df["emotion_score"] = emotion_scores
    df["sentiment"] = sentiments

    df.to_csv(output_file, index=False)
    print(f"Emotion analysis complete on comments.")

