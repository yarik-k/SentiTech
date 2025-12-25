import os
import csv
import json
import re
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("TLDR_API_KEY")

script_dir = os.path.dirname(os.path.abspath(__file__))

transcripts_csv_path = os.path.join(script_dir, "../inputs-outputs/condensed_transcripts.csv")
comments_csv_path = os.path.join(script_dir, "../inputs-outputs/cleaned_youtube_comments.csv")
processed_json_path = os.path.join(script_dir, "../inputs-outputs/analyzed_sentiments.json")
log_file = os.path.join(script_dir, "tldr_output.log")

def load_transcripts(csv_path):
    all_text = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row.get("text")
            transcript_text = row["text"].strip()
            words = transcript_text.split()
            # 150 words max per transcript for token limit
            truncated_words = words[:150]
            truncated_text = " ".join(truncated_words)
            all_text.append(truncated_text)
    return "\n".join(all_text)

def load_comments(csv_path):
    all_comments = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row.get("cleaned_comment")
            all_comments.append(row["cleaned_comment"])

    combined_text = " ".join(all_comments)

    # 300 words max for comment block for token limit
    words = combined_text.split()
    truncated_words = words[:300]
    truncated_text = " ".join(truncated_words)

    return truncated_text

def load_ABSA(json_path):
    all_sentences = []
    with open(json_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)
        for obj in data:
            if obj.get("sentence"):
                all_sentences.append(obj["sentence"])
    
    combined_text = " ".join(all_sentences)
    
    # 400 words max for ABSA block for token limit
    words = combined_text.split()
    truncated_words = words[:400]
    truncated_text = " ".join(truncated_words)
    
    return truncated_text

def generate_summary(all_data):
    prompt = f"""
    Output ONE JSON object with three short fields that cover 3 VERY SHORT summaries:

    "summary": A TL;DR high-level summary of everything (2 sentences).
    "risk": A short product safety and risk assessment across all the data (1 sentence).
    "recommendation": Whether the user should buy the product or not (1-2 sentences) (concise recommendation BASED ON THE DATA primarily, other knowledge can be used for this if it is critical to the analysis).

    Keep it minimal in length (fewer than 150 words total).

    Here's all the text you have access to:

    --- BEGIN DATA ---
    {all_data}
    --- END DATA ---

    Now produce the JSON object with every field:
    """

    response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "You summarize product data and provide risk and buy/do-not-buy recommendation."}, {"role": "user", "content": prompt}], temperature=0.7, max_tokens=300)
    raw_text = response.choices[0].message.content.strip()

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # because some cases threw errors with old logic
    summary_match = re.search(r'"summary"\s*:\s*"(.+?)"', raw_text, re.DOTALL)
    risk_match = re.search(r'"risk"\s*:\s*"(.+?)"', raw_text, re.DOTALL)
    recommendation_match = re.search(r'"recommendation"\s*:\s*"(.+?)"', raw_text, re.DOTALL)

    summary = summary_match.group(1).strip() if summary_match else ""
    risk = risk_match.group(1).strip() if risk_match else ""
    recommendation = recommendation_match.group(1).strip() if recommendation_match else ""

    output = "\n".join([summary, risk, recommendation])
    print(output)

if __name__ == "__main__":
    transcripts_text = load_transcripts(transcripts_csv_path)
    comments_text = load_comments(comments_csv_path)
    processed_text = load_ABSA(processed_json_path)

    combined_text = "\n".join([transcripts_text, comments_text, processed_text])

    generate_summary(combined_text)

