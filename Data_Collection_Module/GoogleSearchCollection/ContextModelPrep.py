import os
import re
import json
import spacy
from transformers import DebertaTokenizer

# load SpaCy NLP for tokenization
nlp = spacy.load("en_core_web_sm")  

# load tokenizer
# tokenizer = DebertaTokenizer.from_pretrained("microsoft/deberta-large")
# REMOVED TOKENIZER - changed model in upcoming sentiment analysis, this is redundant

script_dir = os.path.dirname(os.path.abspath(__file__))

texts_directory = os.path.join(script_dir, "../../inputs-outputs/sentiment_ready_texts")
output_file = os.path.join(script_dir, "../../inputs-outputs/processed_dataset.json")

REMOVE_PATTERNS = [
    r"you are using an out of date browser.*?",
    r"this sidebar will go away.*?",
    r"http\S+|www\S+",  # remove URLs
    r"\s+",  # normalize extra spaces
    r"\[.*?\]",  # remove text inside square brackets (e.g., [deleted])
    r"^\W*$",  # remove non-word characters (like "-----")
    r"^\d+$",  # remove isolated numbers
    r"\b(thanks|hello|hi|goodbye|bye|ok|okay|hmm|huh|yeah|nope|idk)\b",  # remove common chat noise
    r"\b(i guess|i think|i feel|maybe|perhaps|sort of|kind of|not sure)\b"  # remove hesitation phrases
]

# clean text for removal patterns
def clean_text(text):
    for pattern in REMOVE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    return text

# merging short sentences while keeping longer sentences intact with a buffer
# effective but can merge consequent unrelated sentences and skew analysis
def merge_sentences(sentences):
    merged_sentences = []
    sentence_buffer = ""

    for sentence in sentences:
        if len(sentence) < 40:
            sentence_buffer += " " + sentence
        else:
            if sentence_buffer:
                merged_sentences.append(sentence_buffer.strip())
                sentence_buffer = ""
            merged_sentences.append(sentence)

    if sentence_buffer:
        merged_sentences.append(sentence_buffer.strip())

    return merged_sentences

# tokenize sentences with SpaCy and merge
def split_sentences(text):
    doc = nlp(text) 
    sentences = []
    for sent in doc.sents: # relying on SpaCy doc.sents to reliably tokenize into sentences
        sentences.append(sent.text.strip())

    return merge_sentences(sentences)

def build_dataset():
    dataset = []
    
    for filename in os.listdir(texts_directory):
        filepath = os.path.join(texts_directory, filename)

        if not os.path.isfile(filepath) or filename.startswith('.'):
            continue

        with open(filepath, "r", encoding="utf-8", errors="replace") as file:
            raw = file.read()
        
        cleaned = clean_text(raw)
        split_sents = split_sentences(cleaned)

        if not split_sents:
            continue

        # tokenized_sentences = tokenizer(split_sents, padding="longest", truncation=True, max_length=512, return_tensors="pt")

        for i, sent in enumerate(split_sents):
            # input_ids = tokenized_sentences["input_ids"][i].tolist()
            # attention_mask = tokenized_sentences["attention_mask"][i].tolist()

            dataset.append({
                "filename": filename, "original_text": sent, # "tokenized_input_ids": input_ids, "tokenized_attention_mask": attention_mask
            })

    return dataset

if __name__ == "__main__":
    # build and save the dataset
    dataset = build_dataset()

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=4)
    except Exception as e:
        print(f"Error opening file: {e}")

    print(f"Processed dataset successfully saved.")
