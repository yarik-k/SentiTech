import json
import os
import sys
import openai
import csv
import re
from progress_tracking import update_progress
import requests
from dotenv import load_dotenv

load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))

comparison_file = os.path.join(script_dir, "../inputs-outputs/comparison_output.txt")
best_features_file = os.path.join(script_dir, "../inputs-outputs/best_features.txt")

def build_comparison_prompt(product_name):
    return f"""
  You are a comparison generator. The user has given you one target product: {product_name}.

  1) Identify 4 direct competitor products (similar release period, price bracket, rival to product, same calibre). Each product must be from a different brand/company, and CANNOT be from the target product brand.
  2) For each competitor plus the original product, generate 7 relevant product features which are the consistent across ALL collected products. E.g for a laptop - display, gpu, cpu, etc..., for a smartphone - battery, camera, screen, etc... . The features must be useful to a customer assessing whether they want to buy the product or not, pick the features carefully so they are relevant. Always include Price as the first feature in GBP (Great British Pounds) WITH the pound sign. Also avoid using features that are standard and the same across all of the products, THIS IS IMPORTANT, try to pick relevant useful features that are different across products. Get the most precise data for each feature and DO NOT leave any cell blank.
  3) Make sure the target product is always first. Also make sure that it is an exact full product name, not a shortened one. You may also be given a base model - e.g IPhone 16, treat this as a base model and its full name.
  4) Additionally under all of this, I want you to add another section outlining which product has the best feature from each row. In the format: Product - Feature - Reason, where "Reason" is a brief explaination of why you chose this as the best feature. Where each best feature is on a new line. You MUST pick a best product for EVERY feature that is present, the same product may be selected for more than one feature. Make sure that you are critical in choosing the best feature and that it is correct compared to the other features in the row. If most features are similar in the row, still pick the best one and explain why it is the best performing.

  Get the most up-to-date and accurate data available as of today. Use current pricing and technical specifications from trusted and official sources (e.g., manufacturer websites, major retailers). DO NOT leave any cell blank, and do NOT include outdated models or prices. Make sure all specs and pricing reflect the latest information publicly available.
  For every feature value, do not return raw numbers without context. Always return values with clear unit labels.

  Return a JSON object in the EXACT following format:

  {{
    "product": "{product_name}",
    "comparison": [
      {{
        "name": "{product_name}",
        "Price (GBP)": "£<price>",
        "Feature 2": "<value>",
        "Feature 3": "<value>",
        "Feature 4": "<value>",
        "Feature 5": "<value>",
        "Feature 6": "<value>",
        "Feature 7": "<value>"
      }},
      {{
        "name": "<generated rival product name>",
        "Price (GBP)": "£<price>",
        "Feature 2": "<value>",
        "Feature 3": "<value>",
        "Feature 4": "<value>",
        "Feature 5": "<value>",
        "Feature 6": "<value>",
        "Feature 7": "<value>"
      }},
      {{
        "name": "<generated rival product name>",
        "Price (GBP)": "£<price>",
        "Feature 2": "<value>",
        "Feature 3": "<value>",
        "Feature 4": "<value>",
        "Feature 5": "<value>",
        "Feature 6": "<value>",
        "Feature 7": "<value>"
      }},
      {{
        "name": "<generated rival product name>",
        "Price (GBP)": "£<price>",
        "Feature 2": "<value>",
        "Feature 3": "<value>",
        "Feature 4": "<value>",
        "Feature 5": "<value>",
        "Feature 6": "<value>",
        "Feature 7": "<value>"
      }},
      {{
        "name": "<generated rival product name>",
        "Price (GBP)": "£<price>",
        "Feature 2": "<value>",
        "Feature 3": "<value>",
        "Feature 4": "<value>",
        "Feature 5": "<value>",
        "Feature 6": "<value>",
        "Feature 7": "<value>"
      }}
    ],
    "best_features": [
      {{
        "feature 1": "Price (GBP)",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }},
      {{
        "feature 2": "<feature name>",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }},
      {{
        "feature 3": "<feature name>",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }},
      {{
        "feature 4": "<feature name>",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }},
      {{
        "feature 5": "<feature name>",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }},
      {{
        "feature 6": "<feature name>",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }},
      {{
        "feature 7": "<feature name>",
        "product": "<product with best feature>",
        "reason": "<short reason>"
      }}
    ]
  }}

  Again you MUST pick a best feature for every feature, so avoid picking features that are the exact same across all products.

  Return only the JSON object and nothing else. Do not add explanations, markdown, or surrounding text.
    """

def call_perplexity(product_name):
    prompt = build_comparison_prompt(product_name)

    url = "https://api.perplexity.ai/chat/completions"
    headers = { "Authorization": f"Bearer {os.getenv("PERPLEXITY_API_KEY")}", "Content-Type": "application/json"} # key to hide
    payload = { "model": "sonar", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3} # adjusted temp for precision

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        output = response.json()
        return output["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"Error calling perplexity: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Input product name as the second argument.")
        sys.exit(1)

    product = sys.argv[1]
    print(f"Requesting comparison data from Perplexity.")
    raw_response = call_perplexity(product)

    if raw_response.startswith("```json"):
        raw_response = raw_response.replace("```json", "").replace("```", "").strip()
    elif raw_response.startswith("```"):
        raw_response = raw_response.replace("```", "").strip()

    try:
      data = json.loads(raw_response)
    except Exception as e:
        print(f"Error opening json file: {e}")

    # debugging
    print(json.dumps(data, indent=2))

    # formatting in text form for backend conversion from old logic
    try:
        with open(comparison_file, "w", encoding="utf-8") as f:
            for item in data.get("comparison", []):
                f.write(f"Product: {item['name']}\n")
                for key, value in item.items():
                    if key != "name":
                        f.write(f"{key}: {value}\n") # formatted in expected text form
                f.write("\n")
        print("Saved the comparison data successfully.")
    except Exception as e:
        print(f"Error handling file: {e}")

    try:
        with open(best_features_file, "w", encoding="utf-8") as f:
            for item in data.get("best_features", []):
                feature_name = item.get("feature 1") or item.get("feature 2") or item.get("feature 3") or item.get("feature 4") or item.get("feature 5") or item.get("feature 6") or item.get("feature 7") or item.get("feature 8") # fixed features names not appearing
                product = item.get("product")
                reason = item.get("reason")
                if feature_name and product and reason:
                    f.write(f"{product} - {feature_name} - {reason}\n")
        print("Saved the best features successfully.")
    except Exception as e:
        print(f"Error handling file: {e}")

    update_progress("comparison", 100)