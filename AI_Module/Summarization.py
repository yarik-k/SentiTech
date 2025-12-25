import json
import os
import time
import re
import openai
import pandas as pd
from nltk.tokenize import sent_tokenize
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from progress_tracking import update_progress
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("SUMMARIZATION_API_KEY")

# Use relative path for portability
script_dir = os.path.dirname(os.path.abspath(__file__))
inputs_outputs_directory = os.path.join(script_dir, "../inputs-outputs/")
comments_file = os.path.join(inputs_outputs_directory, "cleaned_youtube_comments.csv")
ABSA_file = os.path.join(inputs_outputs_directory, "processed_dataset.json")
output_file = os.path.join(inputs_outputs_directory, "both_summaries.txt")

changed_files = set()

# Added watchdog functionality with AI for file tracking

def load_comments():
    try:
        df = pd.read_csv(comments_file)
        comments = df["cleaned_comment"].dropna().tolist()
        return " ".join(comments[:100])  # limited for token size
    except Exception as e:
        print(f"Error opening file: {e}")
        return ""

def load_sentences(json_filepath):
    time.sleep(3) # fix for loading massive file being cut off after observer

    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error opening file: {e}")
        return ""

    all_sentences = [sent_tokenize(entry.get("original_text", "")) for entry in data]
    all_sentences = [s for list in all_sentences for s in list]  # flatten list fixed

    return " ".join(all_sentences[:100]) # adjustable max for token limit (100 sentences)

def generate_summaries(comments_text, sentences_text):
    system_content = (
        "You are a helpful assistant that summarizes discussions to derive useful insights. "
        "The summary must be about the most discussed product (target product) and this product only. "
        "The summary must be balanced and weigh pros and cons critically."
        "The summary must be in a conversational tone, understandable by a regular consumer."
        "Each summary must highlight different pros and cons for the target product, the summaries MUST NOT talk about the same things, this is important."
        "You will be given two blocks of text, each for a separate summary.\n"
        "Please output them in the form:\n\n"
        "=== Summary for Comments ===\n"
        "<summary>\n"
        "=== Summary for Sentences ===\n"
        "<summary>\n"
    )

    data_content = (
        f"BLOCK 1 (Comments):\n{comments_text}\n\n"
        f"BLOCK 2 (Sentences):\n{sentences_text}\n\n"
        "Please provide a 150-word summary of BLOCK 1, then a 150-word summary of BLOCK 2. "
        "Label them exactly as '=== Summary for Comments ===' and '=== Summary for Sentences ==='."
    )

    response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_content}, {"role": "user", "content": data_content}], temperature=0.7)
    output = response.choices[0].message.content

    print(f"GPT Response: {output}")

    return output

def run_summarization(observer):
    print("Running summarization...")

    comments_content = load_comments()
    sentences_text = load_sentences(ABSA_file)

    combined_summaries = generate_summaries(comments_content, sentences_text)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write(combined_summaries + "\n")

    update_progress("summary", 100)

    print(f"AI Summarization done")

    # Stop observer now that both files have changed
    observer.stop()
    print("Stopping observer after detecting changes in both files.")

class InputFilesEventHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer
        self.files_changed = set()

    def on_modified(self, event):
        if event.is_directory:
            return

        changed_file = os.path.abspath(event.src_path)

        if changed_file in {comments_file, ABSA_file}:
            self.files_changed.add(changed_file)
            print(f"Detected change in: {changed_file}")

        # Run summarization only when BOTH files have changed
        if {comments_file, ABSA_file}.issubset(self.files_changed):
            run_summarization(self.observer)

    def on_created(self, event):
        self.on_modified(event)  # Treat newly created files the same as modified ones

if __name__ == "__main__":
    # added manual watchdog observer, watch until changes are detected -> new product search with new output files
    # run summarization on newly loaded data
    observer = Observer()
    handler = InputFilesEventHandler(observer)
    observer.schedule(handler, path=inputs_outputs_directory, recursive=False)

    observer.start()

    while observer.is_alive():
        time.sleep(1)

    observer.join()
