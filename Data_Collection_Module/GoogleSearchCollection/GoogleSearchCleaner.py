import os
import re
import spacy

# SpaCY NLP model for sentence-level tokenization
nlp = spacy.load("en_core_web_sm")

script_dir = os.path.dirname(os.path.abspath(__file__))
input_directory = os.path.join(script_dir, "../../inputs-outputs/scraped_texts")
output_directory = os.path.join(script_dir, "../../inputs-outputs/sentiment_ready_texts")

NOISE_PATTERNS = [
    r"https?://\S+",  # remove URLs
    r"\b(\d{1,2} [A-Za-z]+ \d{4})\b",  # remove dates
    r"\b(Posted on|Updated on|Published on)\b.*",  # remove timestamps
    r"\b(Page|Article|Share|Link|Email|Facebook|Twitter|Reddit)\b.*",  # remove social media tags
    r"\b(Reporter|Editor|Contributor|Author|Review|News|Shopping|Journalist)\b.*",  # remove author details
]

# filtering relevant sentences for sentiment analysis
def extract_sentences(text):
    doc = nlp(text)
    sentences = []

    for sent in doc.sents:
        sentence = sent.text.strip()

        for pattern in NOISE_PATTERNS:
            if re.search(pattern, sentence, re.IGNORECASE):
                continue
        
        # iterate tokens and look for adjectives or verbs skipping punctiation, else discard
        passed_sent = False
        for token in sent:
            if token.is_alpha and token.pos_ in ["ADJ", "VERB"]:
                passed_sent = True
                break
        
        if passed_sent:
            cleaned_sentence = re.sub(r"[^a-zA-Z0-9.,!?'\s]", "", sentence).lower()  # removal of special chars and lower sentence
            sentences.append(cleaned_sentence)

    return "\n".join(sentences)

if __name__ == "__main__":
    # process files
    for filename in os.listdir(input_directory):
        if filename.startswith('.') or not filename.endswith('.txt'): # fix for script reading DS_STORE
            continue

        input_filepath = os.path.join(input_directory, filename)
        output_filepath = os.path.join(output_directory, filename)

        try:
            with open(input_filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            processed_text = extract_sentences(raw_text)

            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(processed_text)

            print("Successfully cleaned sentences.")
        except Exception as err:
            print(f"Error while cleaning: {err}")