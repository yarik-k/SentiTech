import logging
import os
import spacy
import json
import re
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import sys
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nlp = spacy.load("en_core_web_sm")

device = torch.device("mps")

sentiment_model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
sentiment_tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer, device=device)

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "../inputs-outputs/processed_dataset.json")
output_file = os.path.join(script_dir, "../inputs-outputs/analyzed_sentiments.json")
snippets_log = os.path.join(script_dir, "snippets_log.txt")

with open(snippets_log, "w") as f:
    pass

sid = SentimentIntensityAnalyzer()

product_name = None

TECH_ASPECTS = {
    # Display & Screen
    "display": [
        "screen", "display", "brightness", "peak brightness", "contrast", "contrast ratio",
        "resolution", "refresh rate", "color accuracy", "HDR", "glare", "touchscreen",
        "OLED", "LCD", "Mini LED", "MicroLED", "AMOLED", "viewing angles", "screen size",
        "pixel density", "aspect ratio", "curved display", "ambient light sensor",
        "anti-reflective", "blue light filter", "flicker-free", "matte finish", "edge-to-edge",
        "in-cell touch", "dual display", "3D display", "nit", "nits"
    ],

    # Performance
    "performance": [
        "performance","speed", "lag", "efficiency", "responsiveness", "multitasking", "processing power",
        "CPU", "GPU", "RAM", "thermal performance", "overheating", "frame rate",
        "rendering speed", "benchmark scores", "clock speed", "turbo boost", "core count",
        "hyper-threading", "instruction throughput", "latency", "parallel processing",
        "system responsiveness", "bottleneck", "real-time performance", "performance mode"
    ],

    # Battery & Power Management
    "battery": [
        "battery", "battery life", "charge time", "power consumption", "fast charging",
        "wireless charging", "battery drain", "energy efficiency", "wattage", "power adapter",
        "battery capacity", "battery degradation", "battery cycle count", "removable battery",
        "charging efficiency", "battery backup", "endurance", "battery health",
        "charging port", "wired charging", "power brick", "power cable", "quick charge",
        "lasted", "longer battery", "power-saving mode", "power saver",
        "battery drain", "battery optimization", "battery longevity", "power backup",
        "battery endurance", "battery usage", "battery saver feature", "quick battery drain",
        "long-lasting charge", "overnight battery life", "slow discharge"
    ],

    # Storage & SSD
    "storage": [
        "SSD", "HDD", "storage capacity", "read speed", "write speed", "load times",
        "expandable storage", "NVMe", "PCIe", "external storage", "SD card",
        "flash memory", "eMMC", "UFS", "HFS+", "file system performance",
        "SATA", "RAID configuration", "disk encryption"
    ],

    # Connectivity & Ports
    "ports": [
        "USB", "USB 2.0", "USB 3.0", "USB-C", "Thunderbolt", "HDMI", "Ethernet", "SD card reader",
        "audio jack", "Wi-Fi", "Bluetooth", "5G", "LTE", "NFC", "Wi-Fi 6", "Wi-Fi 7",
        "network connectivity", "dongle", "VGA", "DisplayPort", "DVI", "microSD slot", "FireWire",
        "MHL", "Mini DisplayPort", "SIM card slot", "RJ45 port"
    ],

    # Keyboard
    "keyboard": [
        "key travel", "key feel", "backlit keyboard", "mechanical switches", "RGB lighting",
        "typing experience", "keyboard layout", "macro keys", "numpad", "scissor switches",
        "chiclet keys", "water-resistant keyboard", "ergonomic design", "key rollover",
        "anti-ghosting", "hot-swappable keys", "programmable macros"
    ],

    # Trackpad & Mouse Input
    "trackpad": [
        "touchpad", "trackpad sensitivity", "multi-touch gestures", "palm rejection",
        "haptic feedback", "scrolling experience", "precision tracking", "force touch",
        "gesture recognition", "trackpoint"
    ],

    # Audio & Sound System
    "audio": [
        "sound", "speaker", "sound quality", "volume", "bass", "treble", "microphone",
        "noise cancellation", "Dolby Atmos", "spatial audio", "headphone jack",
        "bluetooth audio latency", "wireless earbuds support", "audio codec", "sound clarity",
        "frequency response", "balanced audio", "amplifier", "subwoofer", "stereo separation",
        "surround sound"
    ],

    # Design & Build Quality
    "design": [
        "design", "build quality", "materials", "aesthetics", "weight", "thickness", "durability",
        "hinge strength", "bezel", "chassis", "color options", "portability", "carbon fiber",
        "aluminum body", "plastic chassis", "sleek design", "ergonomic design", "form factor",
        "curved design", "industrial design", "finish", "texture", "back cover design",
        "sturdiness", "premium feel", "waterproof rating", "dust resistance"
    ],

    # Software & User Experience
    "software": [
        "software", "operating system", "pre-installed apps", "UI", "UX", "bloatware", "customization",
        "dark mode", "gesture controls", "voice assistant", "AI features", "Windows 11",
        "macOS", "Linux", "ChromeOS", "software updates", "firmware", "OS stability",
        "driver support", "security patches", "app ecosystem", "multitasking support",
        "interface design", "virtual assistant integration", "app store availability"
    ],

    # Cooling & Thermal Management
    "cooling": [
        "cooling","overheating", "fan noise", "heat dissipation", "thermal throttling",
        "liquid cooling", "airflow", "heat pipes", "cooling pad", "vapor chamber",
        "active cooling", "passive cooling", "temperature control", "thermal design power",
        "fan placement", "fan control software"
    ],

    # Camera & Imaging
    "camera": [
        "camera","webcam", "camera resolution", "low-light performance", "autofocus",
        "video quality", "megapixels", "Face ID", "portrait mode", "ultrawide",
        "zoom", "optical image stabilization", "night mode", "depth sensor", "macro capability",
        "color reproduction", "HDR video", "sensor size", "aperture", "white balance",
        "wide-angle lens", "telephoto lens", "4K recording", "8K recording"
    ],

    # Security & Privacy
    "security": [
        "security", "fingerprint scanner", "Windows Hello", "privacy shutter", "TPM chip",
        "encryption", "secure boot", "face recognition", "iris scanner", "biometric security",
        "two-factor authentication", "password protection", "data encryption",
        "firewall settings", "VPN integration", "antivirus compatibility"
    ],

    # Gaming & Graphics
    "gaming": [
        "gaming","ray tracing", "FPS", "VR gaming", "G-Sync", "FreeSync", "input lag",
        "graphics card", "RGB lighting", "game compatibility", "frame rate consistency",
        "latency", "anti-aliasing", "shader performance", "gaming benchmarks",
        "VRR (Variable Refresh Rate)", "DLSS", "FSR (FidelityFX Super Resolution)"
    ],

    # Accessories & Expansion
    "accessories": [
        "accessories","stylus", "pen support", "dock", "external GPU", "external monitor", "VR headset",
        "gaming controller", "webcam cover", "wireless charger", "case", "screen protector",
        "portable charger", "headphone stand", "adapter", "cable management",
        "portable docking station", "keyboard cover", "kickstand", "car mount"
    ],

    # Mobile-Specific Features
    "mobile": [
        "mobile","SIM", "dual SIM", "eSIM", "fast charging", "camera bump", "screen notch",
        "water resistance", "5G connectivity", "foldable display", "biometric sensors",
        "accelerometer", "gyroscope", "compass", "proximity sensor", "GPS", "magnetic sensor",
        "removable battery", "removable back cover", "wireless power share"
    ],

    # AI or Smart Features
    "AI_Features": [
        "AI", "machine learning", "AI upscaling", "chatbot", "predictive text",
        "smart home integration", "automation", "voice recognition", "natural language processing",
        "personal assistant", "recommendation system", "adaptive learning", "context-aware computing",
        "image recognition", "AI-based noise cancellation", "intelligent scene detection"
    ],

    # Cloud & Subscription Services
    "cloud_Services": [
        "cloud storage", "OneDrive", "Google Drive", "iCloud", "Dropbox", "streaming services",
        "gaming cloud", "remote desktop", "cloud backup", "SaaS", "PaaS", "IaaS",
        "subscription model", "licensing fees", "cloud sync", "cloud gaming platform"
    ],

    # Reliability & Longevity
    "reliability": [
        "reliability","long-term performance", "warranty", "customer support", "firmware updates",
        "repairability", "modularity", "build durability", "consistency", "stability",
        "upgradability", "error rate", "mean time between failures", "service plans",
        "extended warranty", "mean time to repair", "hinge"
    ],

    # Sustainability & Environmental Impact
    "sustainability": [
        "sustainability", "energy star rating", "power efficiency", "recyclable materials",
        "eco-friendly packaging", "carbon footprint", "green certifications",
        "EPEAT rating", "renewable materials", "recycled plastics"
    ],

    # Maintenance & Support
    "maintenance_support": [
        "software patches", "driver updates", "tech support", "online help resources",
        "user manual clarity", "replacement parts availability", "official repair centers",
        "third-party repair", "customer service responsiveness", "remote troubleshooting"
    ],
}

PRICING_TERMS = [
    "expensive", "price", "cost", "worth", "value for money", "too costly",
    "cheap", "budget", "overpriced", "reasonable price", "high cost", "cost-effective",
    "premium pricing", "mid-range price", "low cost", "discounted price", "fair deal",
    "money's worth", "not worth it", "steep price", "over-the-top pricing"
]

BRAND_TERMS = [
    "iphone", "apple", "samsung", "galaxy", "pixel", "macbook", "ipad", "oneplus", "sony",
    "xiaomi", "nvidia", "intel", "amd", "microsoft", "surface", "dell", "hp", "lenovo",
    "asus", "acer", "huawei", "honor", "motorola", "alienware", "razer", "logitech",
    "corsair", "msi", "redmi", "oppo", "vivo"
]

def extract_aspects(sentence):
    aspects_found = set()
    lower_sentence = sentence.lower()
    doc = nlp(sentence)

    # first check - noun chunking for then checking for matches
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        for category, keywords in TECH_ASPECTS.items():
            if any(keyword in chunk_text for keyword in keywords):
                aspects_found.add(category)
    
    # second check - direct regex match as SpaCy fails
    for category, keywords in TECH_ASPECTS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", sentence.lower()):
                aspects_found.add(category)

    # additional pricing aspect if detected
    if any(p in lower_sentence for p in PRICING_TERMS):
        aspects_found.add("pricing")

    return list(aspects_found)

def get_snippet_sentiment(snippet):
    # this model returns - 1 - 5 stars for sentiment classification, 1 - very negative, 5 - very positive
    outputs = sentiment_pipeline(snippet, top_k=None)

    top_output = outputs[0]
    label = top_output["label"]

    star = int(label[0])
    score = (star - 3) / 2.0 # mapping to distribution between -1 and 1
    return score

def apply_manual_rules(text_lower, base_score):
    sentiment_score = base_score

    strong_positive_words = [
        "excellent", "fantastic", "amazing", "phenomenal", "incredible", "outstanding",
        "superb", "brilliant", "perfect", "exceptional", "best", "remarkable", "top-notch",
        "seamless", "flawless", "extraordinary", "spectacular", "impressive", "stunning",
        "glorious", "majestic", "wonderful", "genius", "love", "favorite", "go-to",
        "breathtaking", "marvelous", "exquisite", "unmatched", "astounding"
    ]

    strong_negative_words = [
        "terrible", "horrible", "awful", "worst", "disastrous", "nightmare", "hate",
        "dreadful", "horrific", "unbearable", "regret", "trash", "useless", "pointless",
        "frustrating", "ridiculous", "disgusting", "atrocious", "appalling", "displeased",
        "abysmal", "shocking", "cringeworthy", "catastrophic", "really bad"
    ]

    medium_positive_words = [
        "good", "decent", "solid", "effective", "smooth", "useful", "satisfactory",
        "reliable", "fine", "reasonable", "acceptable", "works well", "no issues",
        "handy", "adequate", "serves its purpose", "up to standard"
    ]

    medium_negative_words = [
        "bad", "mediocre", "lackluster", "underwhelming", "subpar", "could be better",
        "disappointing", "not great", "meh", "flawed", "problematic", "issues",
        "annoying", "inconsistent", "glitchy", "hit or miss", "not impressed",
        "just okay", "setback"
    ]

    for w in strong_positive_words:
        if w in text_lower:
            sentiment_score += 0.3
    for w in strong_negative_words:
        if w in text_lower:
            sentiment_score -= 0.4
    for w in medium_positive_words:
        if w in text_lower:
            sentiment_score += 0.2
    for w in medium_negative_words:
        if w in text_lower:
            sentiment_score -= 0.2
    
    # another check for repeated consequent upper caps with regex
    if re.search(r"[A-Z]{4,}", text_lower) and sentiment_score != 0:
        sentiment_score *= 1.1

    # clip to max or min incase sentiment spills over
    sentiment_score = max(-1.0, min(1.0, sentiment_score))
    return round(sentiment_score, 3)

def extract_subclause(doc, aspect_token_id):
    boundary_deps = {"cc", "mark", "punct", "conj"}

    BOUNDARY_WORDS = {
    # --- Coordinating Conjunctions (FANBOYS) ---
    "for", "and", "nor", "but", "or", "yet", "so",
    # --- Common Subordinating Conjunctions (introduce dependent clauses) ---
    "although", "though", "while", "whereas", "if", "unless", "because", "since",
    "when", "whenever", "where", "wherever", "before", "after", "until", "as",
    "that", "whether", "lest", "once", "supposing", "provided", "providing",
    "even", "till", "altho",
    # --- Common Conjunctive Adverbs (connect independent clauses/ideas, show relationship) ---
    "however", "nevertheless", "nonetheless", "still", "conversely", "instead",
    "otherwise", "regardless", "rather",
    "therefore", "consequently", "thus", "hence", "accordingly", "as a result",
    "furthermore", "moreover", "besides", "additionally", "in addition", "also",
    "meanwhile", "meantime", "subsequently", "then", "next", "afterward", "finally",
    "indeed", "namely", "specifically", "for example", "for instance",
    "similarly", "likewise",

    # --- Others often signaling a boundary/shift/condition ---
    "despite", "except", "unlike", "versus", "vs", "concerning", "regarding"
    }

    left_bound = aspect_token_id
    right_bound = aspect_token_id + 1

    # keeping scanning left until boundary found
    while left_bound > 0:
        left_token = doc[left_bound - 1]
        if left_token.is_punct or left_token.dep_ in boundary_deps or left_token.lower_ in BOUNDARY_WORDS:
            break
        left_bound -= 1

    # keeping scanning right until boundary found
    while right_bound < len(doc):
        right_token = doc[right_bound]
        if right_token.is_punct or right_token.dep_ in boundary_deps or right_token.lower_ in BOUNDARY_WORDS:
            break
        right_bound += 1

    return left_bound, right_bound

def get_aspect_snippet(doc, token_id):
    max_window=10

    # step 1 - gather expand small window (2 tokens either side)
    left_min = max(0, token_id - 2)
    right_min = min(len(doc), token_id + 2 + 1)

    snippet_text = doc[left_min:right_min].text
    sentiment = sid.polarity_scores(snippet_text)

    if abs(sentiment["compound"]) >= 0.3:
        return snippet_text

    # step 2 - if small window fails, resort to expanding window with left and right sub-clause
    sub_left, sub_right = extract_subclause(doc, token_id)
    subclause_text = doc[sub_left:sub_right].text

    sentiment = sid.polarity_scores(subclause_text)
    if abs(sentiment["compound"]) >= 0.3:
        return subclause_text

    # step 3 - expand out from subclause boundaries until max_window size either side
    left_bound = sub_left
    right_bound = sub_right

    for counter in range(1, max_window + 1):
        left_expanded = max(0, left_bound - counter)
        right_expanded = min(len(doc), right_bound + counter)

        snippet_text = doc[left_expanded:right_expanded].text
        sentiment = sid.polarity_scores(snippet_text)

        # fallback to final snippet text in last resort if max window reached
        if abs(sentiment["compound"]) >= 0.3 or counter == max_window:
            return snippet_text

    return snippet_text

def get_aspect_sentiment(aspect, sentence):
    doc = nlp(sentence)

    # identifying the token where the aspect is to gather the snippet
    for i, token in enumerate(doc):
        if token.text.lower() in TECH_ASPECTS.get(aspect, []): # fixed iterations breaking on none type
            snippet_text = get_aspect_snippet(doc, i)
            snippet_score = get_snippet_sentiment(snippet_text)
            global_score = get_snippet_sentiment(sentence)

            # debugging to remove
            with open(snippets_log, "a", encoding="utf-8") as f:
                f.write(f"Aspect: {aspect}\nSnippet: {snippet_text}\n\n")

            # adjusted slight weight to global score aswell for long sentences
            combined = 0.90 * snippet_score + 0.10 * global_score
            final_score = apply_manual_rules(sentence.lower(), combined)
            return final_score

    # fallback for no aspects
    global_score = get_snippet_sentiment(sentence)
    final_score = apply_manual_rules(sentence.lower(), global_score)
    return final_score

def get_sentiment(sentence, aspects):
    aspect_scores = {}
    for aspect in aspects:
        aspect_scores[aspect] = get_aspect_sentiment(aspect, sentence)
    return aspect_scores

def is_meaningful(sentence, aspects):
    overall_sent = get_snippet_sentiment(sentence)
    lowered = sentence.lower()

    product_keywords = set(product_name.lower().split())
    partial_product = any(word in lowered for word in product_keywords)

    # contains any aspects and sentiment over 0.5?
    if aspects and abs(overall_sent) > 0.5:
        return True, 0
    
    # contains product words and sentiment > 0.3?
    if partial_product and abs(overall_sent) > 0.3:
        return True, overall_sent

    # contains brand terms and sentiment > 0.5?
    if any(b in lowered for b in BRAND_TERMS) and abs(overall_sent) >= 0.5:
        aspects.append("general")
        return True, overall_sent

    doc = nlp(sentence)
    # final last chance if long sentence and strong sentiment
    if len(doc) >= 15 and abs(overall_sent) >= 0.9:
        aspects.append("general")
        return True, overall_sent

    return False, 0

def process_reviews(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    filtered_results = []
    for entry in dataset:
        sentence = entry.get("original_text", "").strip()
        if not sentence:
            continue

        aspects = extract_aspects(sentence)
        sentiment_scores = get_sentiment(sentence, aspects)

        meaningful, overall_score = is_meaningful(sentence, aspects)

        if meaningful:
            # fixed assign general if no aspect, as aspectless sentences are allowed now
            if("general" in aspects):
                sentiment_scores["general"] = overall_score

            filtered_results.append({"sentence": sentence, "aspects": aspects, "sentiment_scores": sentiment_scores})

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_results, f, indent=4)

    print(f"ABSA successfully completed for Google.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No product name provided.")
        sys.exit(1)

    target_product = sys.argv[1]
    product_name = target_product

    # for debugging
    print(f"Processing reviews.")
    process_reviews(input_file, output_file)