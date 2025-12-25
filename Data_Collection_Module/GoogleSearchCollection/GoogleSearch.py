import os
import sys
import requests
import time
from dotenv import load_dotenv

load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "../../inputs-outputs/google_discussion_links.txt")

# "safe" scrapable discussion sites
allowed_sites = ["techradar.com", "tomshardware.com", "macrumors.com", "forums.overclockers.co.uk", "www.engadget.com", "www.tomsguide.com", "www.overclockers.co.uk", "www.rtings.com"]

def fetch_links(product_name):
    print(f"Searching for reviews and discussions on {product_name}")

    endpoint = "https://www.googleapis.com/customsearch/v1"
    links = []

    # joining trusted sites together for the query
    site_filter = " OR ".join([f"site:{site}" for site in allowed_sites])

    for page in range(3):
        start = page * 10 + 1

        # query construction
        query = {"q": f"{product_name} review OR discussion OR forum ({site_filter})", "key": os.getenv("GOOGLE_SEARCH_API_KEY"), "cx": os.getenv("GOOGLE_SEARCH_ENGINE_ID"), "start": start, "num": 10}

        try:
            res = requests.get(endpoint, params=query, timeout=10)
            data = res.json()

            items = data.get("items")
            if not items:
                print(f"No results on page")
                break

            new_links = []
            for item in items:
                new_links.append(item["link"])
            links.extend(new_links)

            print(f"Page {page + 1}: {len(new_links)} links found.")

            time.sleep(0.5)  # avoiding rate limits and restrictions

        except Exception as err:
            print(f"Error raised: {err}")
            break

    # save the collected links to a file
    with open(output_path, "w", encoding="utf-8") as out_file:
        for url in links:
            out_file.write(url + "\n")
    print(f"Sucessfully saved links to output file.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter product name as a second parameter.")
        sys.exit(1)

    product = sys.argv[1]
    fetch_links(product)
