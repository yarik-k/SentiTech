import ast
import asyncio
import csv
import sys
import concurrent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import pandas as pd
from pydantic import BaseModel
import subprocess
import json
import os
import numpy as np
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re
from nltk.tokenize import sent_tokenize
import ast
from collections import defaultdict
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("BACKEND_API_KEY")

cached_results = None
product_name = None

class ProductRequest(BaseModel):
    product: str

app = FastAPI()

# relative path resolver for project portability - added at very end
script_dir = os.path.dirname(os.path.abspath(__file__))

def path(*parts):
    return os.path.abspath(os.path.join(script_dir, *parts))

# fixed cors issue with AI with certain pages not working
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

google_script = path("../Data_Collection_Module/GoogleSearchCollection/RunAll.py")
youtube_script = path("../Data_Collection_Module/YoutubeCollection/RunAll.py")
summaries_script = path("../AI_Module/Summarization.py")
comparison_script = path("../AI_Module/GetComparison.py")
summaries_output = path("../inputs-outputs/both_summaries.txt")
analyzed_sentiments = path("../inputs-outputs/analyzed_sentiments.json")
processed_comments = path("../inputs-outputs/processed_youtube_comments.csv")
comparison_output = path("../inputs-outputs/comparison_output.txt")
best_features_output = path("../inputs-outputs/best_features.txt")
processed_transcripts = path("../inputs-outputs/processed_youtube_transcripts.csv")
benefits_drawbacks = path("../inputs-outputs/benefits_drawbacks.json")
keywords = path("../inputs-outputs/tech_keywords.json")

def star_rating(sentiment_score, feature_sentiments):
    scores = np.array(feature_sentiments)
    mean_score = np.mean(scores)

    # weighting logic - 0.6 from mean + 0.4 from main score
    combined_score = 0.6 * mean_score + 0.4 * sentiment_score

    if combined_score < 0:
        return 1
    elif combined_score < 0.1:
        return 2
    elif combined_score < 0.3:
        return 3
    elif combined_score < 0.5:
        return 4
    else:
        return 5

def extract_summaries(aspect_text_map, aspect_scores):
    global cached_results

    if not aspect_text_map:
        return {}
    
    aspects = list(aspect_text_map.keys())
    aspects = ", ".join(aspects)

    instructions = (
        f"Below is a collection of aspects, each with a block of text. "
        f"For each aspect, please provide a SINGLE-SENTENCE summary of the text. Provide a summary for EVERY single aspect in this list: {aspects}. If there is not enough information then use your own knowledge for the summary, but always use the data provided primarily."
        f"The summary MUST be about the target product: {product_name}"
        "The summary MUST reflect the aspect score given. If the aspect score is above 75, give a very positive summary of pros ONLY. If the aspect score is between 70 and 90, give a positive summary of pros and rarely include a con if found. If the aspect score is between 45 and 70, give a neutral toned summary of pros and cons. If the aspect score is below 45, give a negative summary of cons."
        "AVOID discussing the same points across multiple features. Prices must be in GBP."
        "Return each aspect name on its own line, with no extra punctuation or bold styling and lowercase, followed by its summary on the next line. Don’t use any markdown, punctuation, or blank lines."
    )

    aspects_json = json.dumps(aspect_text_map, ensure_ascii=False)
    aspects_scores_json = json.dumps(aspect_scores, ensure_ascii=False)
    user_prompt = f"{instructions}\n\nASPECT SCORES:{aspects_scores_json}\n\nASPECTS TEXTS:\n{aspects_json}\n\n"

    # debugging to remove
    with open(path("../Backend_Module/output_prompt"), "w", encoding="utf-8") as f:
        f.write(user_prompt)

    try:
        # gpt-4o-mini (adjustable)
        # adjust temp
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "You are a concise assistant that summarizes text."}, {"role": "user", "content": user_prompt}], temperature=0.4, max_tokens=1200)
        raw_content = response.choices[0].message.content

        # debugging to remove
        with open(path("../Backend_Module/output"), "w", encoding="utf-8") as f:
            f.write(raw_content)

        # fixed strippling and handling lines with AI as this was breaking on cases
        stripped_lines = [line.strip() for line in raw_content.strip().splitlines() if line.strip()]

        summary_dict = {}
        i = 0
        while i < len(stripped_lines):
            aspect_line = stripped_lines[i]
            i += 1

            if i < len(stripped_lines):
                summary_line = stripped_lines[i]
                i += 1
            else:
                summary_line = ""

            summary_dict[aspect_line] = summary_line

        return summary_dict
    except Exception as e:
        print(f"Summarization failed: {e}")
        return {}

def process_feature_sentiments(data):
    feature_sentiments = defaultdict(list)
    feature_counts = Counter()
    feature_sentences = defaultdict(list)

    for review in data:
        sentence = review.get("sentence", "").strip()
        sentiment_scores = review.get("sentiment_scores", {})

        for aspect, score in sentiment_scores.items():
            feature_sentiments[aspect].append(score)
            feature_counts[aspect] += 1
            feature_sentences[aspect].append(sentence)

    # group into blocks per aspect, fixed
    aspect_text_map = {}
    for aspect, sents in feature_sentences.items():
        combined_text = " ".join(sents).strip()
        if combined_text:
            aspect_text_map[aspect] = combined_text
    
    # recalculating aspect scores up here from logic below to feed into feature summaries
    aspect_scores = {}
    for aspect, scores in feature_sentiments.items():
        avg_score = np.mean(scores)
        if avg_score < 0.1:
            avg_score = 0.1
        boosted_score = np.sign(avg_score) * (abs(avg_score) ** 0.45)
        aspect_scores[aspect] = boosted_score

    aspect_summaries = extract_summaries(aspect_text_map, aspect_scores)

    with open(path("../Backend_Module/output_summaries"), "w", encoding="utf-8") as f:
        f.write(json.dumps(aspect_summaries, ensure_ascii=False, indent=2))

    feature_summaries = []
    for aspect, scores in feature_sentiments.items():
        avg_score = np.mean(scores)
        
        # boost to 10% if score is really low
        if(avg_score < 0.1):
            avg_score = 0.1

        # further boosting scores - added for normalization (0.45)
        boosted_avg = np.sign(avg_score) * (abs(avg_score) ** 0.45)

        stars = star_rating(avg_score, scores)

        summary = aspect_summaries.get(aspect, "No summary available.")

        feature_summaries.append({"feature": aspect, "sentiment_score": round(boosted_avg, 3), "star_rating": stars, "example_sentence": summary})

    # descending sort optimized with AI from old logic
    feature_summaries = sorted(feature_summaries, key=lambda x: x["sentiment_score"], reverse=True)
    return feature_summaries, dict(feature_counts) 

def run_script(script_path: str, product_name: str):
    try:
        result = subprocess.run(
            ['python3', script_path, product_name],
            capture_output=True, text=True, check=False, env=os.environ.copy()
        )
        stdout_decoded = result.stdout.strip()
        stderr_decoded = result.stderr.strip()

        print(f"\n=== Script Execution: {os.path.basename(script_path)} ===")
        print(f"STDOUT:\n{stdout_decoded}")
        print(f"STDERR:\n{stderr_decoded}\n")

        if result.returncode == 0:
            return {"script": os.path.basename(script_path), "status": "Success", "output": stdout_decoded}
        else:
            return {"script": os.path.basename(script_path), "status": "Error", "error": stderr_decoded}

    except Exception as e:
        return {"script": os.path.basename(script_path), "status": "Execution Failed", "error": str(e)}

def execute_multiple(product_name: str):
    # wipe data - fix for broken progress bar
    progress_data = {"google": 0, "youtube": 0, "summary": 0, "comparison": 0, "completed": False}

    # debugging to remove
    with open(path("../inputs-outputs/progress.json"), "w") as f: 
        json.dump(progress_data, f, indent=2)

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor: # expanded to run all processes required in parallel, control max workers
        future_google = executor.submit(run_script, google_script, product_name)
        future_youtube = executor.submit(run_script, youtube_script, product_name)
        future_summary = executor.submit(run_script, summaries_script, product_name)
        future_comparison = executor.submit(run_script, comparison_script, product_name)

        google_result = future_google.result()
        youtube_result = future_youtube.result()
        summary_result = future_summary.result()
        future_comparison = future_comparison.result()

    return {"product_name": product_name, "result": google_result, "youtube_result": youtube_result, "summary_result": summary_result, "comparison": future_comparison} # redundant as handling changed

@app.post("/api/analyze")
async def analyze_product(data: ProductRequest):
    global product_name
    product_name = data.product.strip()

    # defining globally is unreliable, added optional resort to file with name
    with open(path("../Backend_Module/product_name.txt"), "w", encoding="utf-8") as f:
        f.write(product_name)

    global cached_results
    cached_results = None

    print("Search started.")

    results = await asyncio.to_thread(execute_multiple, product_name)

    return {"product_name": product_name, "result": results["result"], "youtube_result": results["youtube_result"]}

def load_emotion_data():
    df = pd.read_csv(processed_comments)
    return df.to_dict(orient="records")

def process_emotion_distribution(data):
    emotion_sums = Counter()
    emotion_counts = Counter()

    for entry in data:
        emotion_json = entry.get("emotion_analysis", "{}")
        
        try:
            emotion_data = json.loads(emotion_json)
        except Exception:
            continue

        for emotion, score in emotion_data.items():
            emotion_sums[emotion] += score
            emotion_counts[emotion] += 1

    if not emotion_sums:
        return {}
    
    return {emotion: round(emotion_sums[emotion] / emotion_counts[emotion], 4) for emotion in emotion_sums}

def process_sentiment_distribution(data):
    sentiment_counts = {"positive": 0, "mixed": 0, "negative": 0}
    for row in data:
        s = str(row.get("sentiment", "")).lower()
        if s in sentiment_counts:
            sentiment_counts[s] += 1
    return sentiment_counts

def get_sentiment_comments(emotion_data):
    sentiment_comments = defaultdict(list)
    seen = defaultdict(set)

    for row in emotion_data:
        sentiment = str(row.get("sentiment", "")).lower().strip()
        comment = str(row.get("cleaned_comment", "")).strip()
        score = row.get("emotion_score", 0.0)

        # final filter pass before display
        if score < 0.7 or len(comment.split()) <= 20:
            continue

        short_comment = comment[:300] + "..." if len(comment) > 300 else comment

        if short_comment.lower() in seen[sentiment]:
            continue

        sentiment_comments[sentiment].append(short_comment)
        seen[sentiment].add(short_comment.lower())

    return dict(sentiment_comments)

def get_emotion_comments(emotion_data):
    emotion_comments = defaultdict(list)
    seen = defaultdict(set)

    for entry in emotion_data:
        comment = str(entry.get("cleaned_comment", "")).strip()
        best_emotion = str(entry.get("top_emotion", "")).strip()
        best_score = entry.get("emotion_score", 0.0)

        if not comment or not best_emotion:
            continue

        # final filter pass before display
        if best_score < 0.7 or len(comment.split()) <= 20:
            continue
    
        short_comment = comment[:300] + "..." if len(comment) > 300 else comment

        if short_comment.lower() in seen[best_emotion.lower()]:
            continue

        emotion_comments[best_emotion.lower()].append(short_comment)
        seen[best_emotion.lower()].add(short_comment.lower())

    return dict(emotion_comments) # fixed output

def load_summaries():
    with open(summaries_output, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 5:
        raise ValueError("Not enough summary data returned.")

    comment_summary = lines[1].strip()
    google_summary = lines[4].strip()

    return comment_summary, google_summary

def load_comparison_data():
    try:
        with open(comparison_output, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
    except Exception as e:
        print(f"Error opening file: {e}")

    product_blocks = raw_text.split("\n\n")

    comparison_data = []
    for block in product_blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        product_info = {}
        for line in lines:
            # carefully extracting from intended file structure fixed
            parts = line.split(":", maxsplit=1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                product_info[key] = value

        if product_info:
            comparison_data.append(product_info)

    return comparison_data

def load_best_features():
    try:
        with open(best_features_output, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error opening file: {e}")

    best_features = []
    for line in lines:
        parts = line.split(" - ")
        if len(parts) < 3:
            continue

        product_part = parts[0].strip()
        feature_part = parts[1].strip()

        reason_part = parts[2]
        reason_text = reason_part.replace("Reason:", "").strip()

        best_features.append({"product": product_part, "feature": feature_part, "reason": reason_text})

    return best_features

def process_transcripts():
    try:
        df = pd.read_csv(processed_transcripts)
    except Exception as e:
        print(f"Error opening file: {e}")

    # same ast.literal_eval fix for lists loading incorrectly from csv
    df['aspect_sentiments'] = df['aspect_sentiments'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    aspect_count = defaultdict(int)
    aspect_sentiments = defaultdict(lambda: defaultdict(int))

    for aspect_dict in df['aspect_sentiments']:
        for aspect, sentiment_data in aspect_dict.items():
            if 'sentiment_label' in sentiment_data:
                sentiment_label = sentiment_data['sentiment_label']

                aspect_count[aspect] += 1
                
                aspect_sentiments[aspect][sentiment_label] += 1

    # extract top 3 most mentioned
    top_aspects = sorted(aspect_count, key=aspect_count.get, reverse=True)[:3]

    # normalizing for piechart display
    final_results = {}
    for aspect in top_aspects:
        sentiment_counts = aspect_sentiments[aspect]
        total = sum(sentiment_counts.values())
    
        aspect_result = {}
        for sentiment, count in sentiment_counts.items():
            proportion = count / total # proportion relative to total counts
            aspect_result[sentiment] = round(proportion, 3)
        
        final_results[aspect] = aspect_result

    return final_results

def load_benefits_drawbacks():
    with open(benefits_drawbacks, 'r') as file:
        data = json.load(file)
    return data.get("top_benefits", []), data.get("top_drawbacks", [])

def load_keywords():
    with open(keywords, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {}
    for item in data.get("tech_keywords", []):
        key = item["keyword"]
        value = item["significance"]
        result[key] = value

    return result

def calculate_stats():
    stats = {}

    with open(path("../inputs-outputs/google_discussion_links.txt"), 'r', encoding='utf-8') as f:
        google_sites = len(f.readlines())
    stats['google_sites_processed'] = google_sites

    with open(path("../inputs-outputs/analyzed_sentiments.json"), 'r', encoding='utf-8') as f:
        sentiments = json.load(f)

    total_sentences = 0
    for entry in sentiments:
        if entry["sentence"]:
            total_sentences += 1
    stats["sentences_analyzed"] = total_sentences

    with open(path("../inputs-outputs/youtube_comments.csv"), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # fixed header
        total_rows = 0
        for row in reader:
            total_rows += 1
    stats["youtube_comments_total"] = total_rows

    with open(path("../inputs-outputs/cleaned_youtube_comments.csv"), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        cleaned_total = 0
        for row in reader:
            cleaned_total += 1
    stats["youtube_comments_filtered"] = cleaned_total

    with open(path("../inputs-outputs/youtube_transcripts.csv"), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        word_count = 0
        for row in reader:
            if "transcript" in row and row["transcript"]:
                words = row["transcript"].split()
                word_count += len(words)
    stats["transcript_word_count"] = word_count

    with open(path("../inputs-outputs/cleaned_youtube_transcripts.csv"), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        word_count = 0
        for row in reader:
            if "sentence" in row and row["sentence"]:
                words = row["sentence"].split()
                word_count += len(words)
    stats["cleaned_transcript_word_count"] = word_count

    return stats

def run_tldr():
    result = subprocess.run(["python3", path("../AI_Module/TLDR-LLM.py")], capture_output=True, text=True)

    raw_text = result.stdout

    with open(path("../Backend_Module/tldr_output.log"), "w", encoding="utf-8") as f:
        f.write(raw_text)

    lines = raw_text.split('\n')

    return lines

def get_product_name():
    with open(path("../Backend_Module/product_name.txt"), "r", encoding="utf-8") as f:
        return f.read().strip()

@app.get("/api/progress")
async def get_progress():
    with open(path("../inputs-outputs/progress.json"), "r") as f:
        progress_data = json.load(f)
    return progress_data

@app.get("/api/results")
async def get_results():
    global product_name
    if not product_name:
        product_name = get_product_name()

    global cached_results

    if cached_results is not None:
        return cached_results

    try:
        with open(analyzed_sentiments, "r") as f:
            data = json.load(f)

        positive_count, negative_count, neutral_count = 0, 0, 0

        for review in data:
            for score in review.get("sentiment_scores", {}).values():
                # 0.2 space for neutrality adjusted, -0.1 < x < 0.1
                if score > 0.1:
                    positive_count += 1
                elif score < -0.1:
                    negative_count += 1
                else:
                    neutral_count += 1

        total = positive_count + negative_count + neutral_count

        if total > 0:
            positive_percentage = round((positive_count / total) * 100, 2)
            negative_percentage = round((negative_count / total) * 100, 2)
            neutral_percentage = round((neutral_count / total) * 100, 2)

            total_percentage = positive_percentage + negative_percentage + neutral_percentage
            # if slight overflow append to neutral percentage to prevent errors
            if total_percentage != 100.0:
                adjustment = 100.0 - total_percentage
                neutral_percentage += round(adjustment, 2)
        else:
            positive_percentage, negative_percentage, neutral_percentage = 0, 0, 0

        # data for feature summary
        feature_summary, feature_frequencies = process_feature_sentiments(data)

        # adjusted to strictly include feature summaries with 10+ mentions for data diversity
        feature_summary = [fs for fs in feature_summary if feature_frequencies.get(fs["feature"], 0) >= 10]

        emotion_data = load_emotion_data()

        # emotion distributions and comments
        emotion_distribution = process_emotion_distribution(emotion_data)
        sentiment_distribution = process_sentiment_distribution(emotion_data)

        sentiment_comments = get_sentiment_comments(emotion_data)
        emotion_comments = get_emotion_comments(emotion_data)

        # data for summaries
        comment_summary, google_summary = load_summaries()

        # data for comparison tool
        comparison_data = load_comparison_data()
        best_features_data = load_best_features()

        # transcripts data
        transcript_distributions = process_transcripts()
        benefits_drawbacks = load_benefits_drawbacks()
        keywords_dict = load_keywords()

        data_statistics = calculate_stats()

        tldr_lines = run_tldr()

        cached_results = {
            "product_name": product_name,
            "positive_percentage": positive_percentage,
            "negative_percentage": negative_percentage,
            "neutral_percentage": neutral_percentage,
            "features": feature_summary,
            "feature_frequencies": feature_frequencies,
            "overall_emotion_distribution": emotion_distribution,
            # "aspect_emotion_distribution": aspect_emotion_distribution,
            "sentiment_distribution": sentiment_distribution,
            "sentiment_comments": sentiment_comments,
            "emotion_comments": emotion_comments,
            "comment_summary": comment_summary,
            "google_summary": google_summary,
            "comparison_data": comparison_data,
            "best_features": best_features_data,
            "transcript_distributions": transcript_distributions,
            "benefits_drawbacks": benefits_drawbacks,
            "keywords_dict": keywords_dict,
            "data_statistics": data_statistics,
            "tldr_lines": tldr_lines
        }
        return cached_results
    except Exception as e:
        print(f"Error calculating results: {e}")
