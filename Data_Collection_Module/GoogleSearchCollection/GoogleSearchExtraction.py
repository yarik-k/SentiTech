import requests
from bs4 import BeautifulSoup
import os
import time

# paths
script_dir = os.path.dirname(os.path.abspath(__file__))
links_file = os.path.join(script_dir, "../../inputs-outputs/google_discussion_links.txt")
output_directory = os.path.join(script_dir, "../../inputs-outputs/scraped_texts")

def extract_text(url):
    # a random copied user-agent to bypass potential blocks, expand
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # clean out non-content tags with no sentiment value
        for tag in soup.find_all(["script", "style", "footer", "header", "nav", "meta", "iframe", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        # filter short / noisy lines and duplicate lines holding little sentiment value
        lines = text.splitlines()
        cleaned = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if len(line) > 50 and line not in seen:
                cleaned.append(line)
                seen.add(line)

        return "\n".join(cleaned)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

# main scraping logic
if __name__ == "__main__":
    with open(links_file, "r", encoding="utf-8") as f:
        urls = f.read().splitlines()

    for i, url in enumerate(urls):
        extracted_text = extract_text(url)

        if extracted_text is None:
            continue

        filename = os.path.join(output_directory, f"site_{i + 1}.txt") # fixed formatting to ensure site names are picked up
        with open(filename, "w", encoding="utf-8") as out:
            out.write(extracted_text)
