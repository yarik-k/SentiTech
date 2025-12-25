import os
import sys
import openai
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("TRANSCRIPT_API_KEY")

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, '../inputs-outputs/condensed_transcripts.csv')
benefits_drawbacks_file = os.path.join(script_dir, '../inputs-outputs/benefits_drawbacks.json')
keywords_file = os.path.join(script_dir, '../inputs-outputs/tech_keywords.json')

system_prompt = """
    You are a product review analysis assistant specialized in parsing video transcripts of tech enthusiasts about the target product: {product_name}.
    Your task is to:
    1. Extract the top 5 most important BENEFITS of the product from the transcript derived from enthusiast opinions.
    2. Extract the top 5 most important DRAWBACKS or CONS of the product from the transcript derived from enthusiast opinions.
    3. Identify and list the 20 most relevant TECHNICAL KEYWORDS frequently used by enthusiasts when reviewing the product, focused on features, specs, and performance terms.

    For each of the benefits and drawbacks, it is important that use a conversational tone that is understandable to a regular consumer aswell, not just a tech enthusiast.
    For each of the benefits and drawbacks, DO NOT add any additional styling or bullets, just text.

    For each technical keyword, assign a "significance rating" based on:
    - Frequency of mention
    - Contextual importance in the review
    - Relevance to product performance or user experience

    The significance rating should range from 1 to 10, where:
    - 10 = extremely significant (high frequency and importance)
    - 1 = minimally significant (low frequency or importance)

    Ensure the output is structured in a JSON format with two sections:
    {
    "benefits_drawbacks": {
        "top_benefits": [...],
        "top_drawbacks": [...]
    },
    "tech_keywords": [
        {"keyword": "example_keyword", "significance": 8},
        ...
    ] 
    }
    Be concise but capture the essence of the enthusiast opinions.
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter a product name as a second argument.")
        sys.exit(1)

    product_name = sys.argv[1]

    df = pd.read_csv(input_file)
    transcript_text = ' '.join(df['text'].dropna().tolist())
    
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": transcript_text}], temperature=0.3)
    response_text = response.choices[0].message.content

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "").replace("```", "").strip()
    elif response_text.startswith("```"):
        response_text = response_text.replace("```", "").strip()

    try:
        data = json.loads(response_text)
    except Exception as e:
        print("Error loading json: ", e)

    with open(benefits_drawbacks_file, 'w') as f:
        json.dump(data['benefits_drawbacks'], f, indent=4)

    with open(keywords_file, 'w') as f:
        json.dump({"tech_keywords": data['tech_keywords']}, f, indent=4)

    print("Transcript LLM script done.")
