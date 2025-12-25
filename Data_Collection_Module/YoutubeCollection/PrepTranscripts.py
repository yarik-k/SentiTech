import os
import pandas as pd
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import spacy

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "../../inputs-outputs/youtube_transcripts.csv")
output_file = os.path.join(script_dir, "../../inputs-outputs/cleaned_youtube_transcripts.csv")

aspect_keywords = {
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
        "performance", "speed", "lag", "efficiency", "responsiveness", "multitasking", "processing power",
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
        "charging port", "wired charging", "power brick", "power cable", "quick charge"
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
        "gesture recognition", "trackpoint","mouse DPI", "tracking accuracy", "ergonomics", "click latency", "wireless mouse",
        "mechanical buttons", "RGB customization", "programmable buttons", "optical sensor",
        "laser sensor", "battery life", "wireless range", "polling rate", "rechargeable battery"
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
        "cooling", "overheating", "fan noise", "heat dissipation", "thermal throttling",
        "liquid cooling", "airflow", "heat pipes", "cooling pad", "vapor chamber",
        "active cooling", "passive cooling", "temperature control", "thermal design power",
        "fan placement", "fan control software"
    ],

    # Camera & Imaging
    "camera": [
        "camera", "webcam", "camera resolution", "low-light performance", "autofocus",
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
        "gaming", "ray tracing", "FPS", "VR gaming", "G-Sync", "FreeSync", "input lag",
        "graphics card", "RGB lighting", "game compatibility", "frame rate consistency",
        "latency", "anti-aliasing", "shader performance", "gaming benchmarks",
        "VRR (Variable Refresh Rate)", "DLSS", "FSR (FidelityFX Super Resolution)"
    ],

    # Accessories & Expansion
    "accessories": [
        "accessories", "stylus", "pen support", "dock", "external GPU", "external monitor", "VR headset",
        "gaming controller", "webcam cover", "wireless charger", "case", "screen protector",
        "portable charger", "headphone stand", "adapter", "cable management",
        "portable docking station", "keyboard cover", "kickstand", "car mount"
    ],

    # Mobile-Specific Features
    "mobile": [
        "mobile", "dual SIM", "eSIM", "fast charging", "camera bump", "screen notch",
        "water resistance", "5G connectivity", "foldable display", "biometric sensors",
        "accelerometer", "gyroscope", "compass", "proximity sensor", "GPS", "magnetic sensor",
        "removable battery", "removable back cover", "wireless power share"
    ],

    # AI or Smart Features
    "AI_features": [
        "AI", "machine learning", "AI upscaling", "chatbot", "predictive text",
        "smart home integration", "automation", "voice recognition", "natural language processing",
        "personal assistant", "recommendation system", "adaptive learning", "context-aware computing",
        "image recognition", "AI-based noise cancellation", "intelligent scene detection"
    ],

    # Cloud & Subscription Services
    "cloud_services": [
        "cloud storage", "OneDrive", "Google Drive", "iCloud", "Dropbox", "streaming services",
        "gaming cloud", "remote desktop", "cloud backup", "SaaS", "PaaS", "IaaS",
        "subscription model", "licensing fees", "cloud sync", "cloud gaming platform"
    ],

    # Reliability & Longevity
    "reliability": [
        "reliability", "long-term performance", "warranty", "customer support", "firmware updates",
        "repairability", "modularity", "build durability", "consistency", "stability",
        "upgradability", "error rate", "mean time between failures", "service plans",
        "extended warranty", "mean time to repair"
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

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    return text.strip()

# this works using SpaCy and tokenizes the sentence into tokens with each token holding contextual info. It then iterates over the tokens
# in the sentence and adds each token text and tag to the current chunk. If it finds a splitting dependency in the sentence then it marks it
# as the last known splitting marker. Then when the tokens (words) exceed 30, we either split at the last marker or the hard limit of 30 words.
# Then the chunk is added to the list of chunks and the splitting marker is recalculated as it no longer exists in the next chunk.
# Any left over words and grouped into a shorter sentence and added to the final chunks.
def split_long_sentence_into_chunks(sentence):
    max_words = 30
    sent_doc = nlp(sentence)
    chunks = []

    # We'll store tuples of (token.text, token.dep_) so that we can later recalc markers.
    current_chunk = []
    last_marker_index = None  # index of last token in current_chunk that is a marker

    for token in sent_doc:
        current_chunk.append((token.text, token.dep_))
        if token.dep_ in {"cc", "punct", "mark"}:
            last_marker_index = len(current_chunk) - 1

        if len(current_chunk) >= max_words:
            if last_marker_index is not None:
                # If we found a marker, split at that boundary.
                split_index = last_marker_index + 1
            else:
                # No marker found: force split at max_words.
                split_index = len(current_chunk)
            
            chunk_text = " ".join(t[0] for t in current_chunk[:split_index]).strip()
            chunks.append(chunk_text)
            # Reset current_chunk to the remaining tokens.
            current_chunk = current_chunk[split_index:]
            # Recalculate last_marker_index for the new current_chunk.
            last_marker_index = None
            for i, (_, dep) in enumerate(current_chunk):
                if dep in {"cc", "punct", "mark"}:
                    last_marker_index = i

    # Append any leftover tokens as a chunk.
    if current_chunk:
        chunk_text = " ".join(t[0] for t in current_chunk).strip()
        chunks.append(chunk_text)

    return chunks

def split_sentences(text):
    max_words = 30 # hard-cap to be adjusted

    text = clean_text(text)
    doc = nlp(text)
    raw_sentences = [sent.text.strip() for sent in doc.sents] # spacy sentence splitting as first, not enough for all cases
    all_sentences = []

    for sentence in raw_sentences:
        if len(sentence.split()) <= max_words:
            all_sentences.append(sentence)
        else:
            # extra AI step added due to SpaCy failing on long sentences
            chunks = split_long_sentence_into_chunks(sentence)
            all_sentences.extend(chunks)
    
    filtered_sentences = []

    for sentence in all_sentences:
        score = sia.polarity_scores(sentence)["compound"]
        if abs(score) > 0.4:
            filtered_sentences.append(sentence)

    return filtered_sentences

def is_meaningful(sentence):
    sentence = clean_text(sentence)

    # meaning section for report
    # ignore short
    if len(sentence.split()) < 5:
        return False

    # check sentiment and subjectivity
    sentiment_score = sia.polarity_scores(sentence)["compound"]
    subjectivity = TextBlob(sentence).sentiment.subjectivity

    # check aspect presence
    sentence_lower = sentence.lower()
    aspect_match = False
    for keywords in aspect_keywords.values():
        for keyword in keywords:
            if keyword in sentence_lower:
                aspect_match = True
                break
        if aspect_match:
            break

    # keep if meets threshold or aspect presence
    if abs(sentiment_score) > 0.35 or subjectivity > 0.35:
        return True
    elif aspect_match and abs(sentiment_score) > 0.15:
        return True
    return False

def get_aspect_labels(sentence):
    found_categories = []
    sentence = sentence.lower()
    for category, keywords in aspect_keywords.items():
        if any(k in sentence for k in keywords):
            found_categories.append(category)
    return list(set(found_categories))

if __name__ == "__main__":
    df = pd.read_csv(input_file)

    cleaned_data = []

    for _, row in df.iterrows():
        video_id = row["video_id"]
        title = row["title"]
        transcript = row["transcript"]

        sentences = split_sentences(transcript)

        for sentence in sentences:
            if is_meaningful(sentence):
                aspects = get_aspect_labels(sentence)
                cleaned_data.append({"video_id": video_id, "title": title, "sentence": sentence, "aspect_labels": aspects})

    cleaned_df = pd.DataFrame(cleaned_data)
    filtered_df = cleaned_df[cleaned_df["aspect_labels"].apply(len) > 0] # filtered out lines with no aspects at all, redundant data appearing

    filtered_df.to_csv(output_file, index=False)
    print(f"Transcripts cleaned successfully.")
