import os
import sys
import emoji
import pandas as pd
import re
from textblob import TextBlob

if len(sys.argv) < 2:
        print("Error: No product name provided.")
        sys.exit(1)

target_product = sys.argv[1]

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "../../inputs-outputs/youtube_comments.csv")
output_file = os.path.join(script_dir, "../../inputs-outputs/cleaned_youtube_comments.csv")

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

def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r'@\w+', '', text)  # Remove mentions
    text = re.sub(r':[a-zA-Z0-9_]+:', '', text) # remove tags in :tag:
    text = re.sub(r'http\S+|www\S+', '', text)  # Remove links
    text = re.sub(r'[^a-zA-Z0-9.,!?\'" ]+', '', text)  # Keep only readable characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

# match aspects substrings to comment text
def find_aspects(comment):
    aspects = []
    comment_lower = comment.lower()

    for category, words in TECH_ASPECTS.items():
        for w in words:
            if w in comment_lower:
                aspects.append(category)
                break  # no double counting - could expand for aspect counts
        
    return ", ".join(aspects) if aspects else None

def is_meaningful(comment):
    if len(comment.split()) < 5:  # filtering very short comments as they don't yield in-depth insights
        return False

    sentiment_score = TextBlob(comment).sentiment.polarity # judge by sentiment polarity
    has_aspect = bool(find_aspects(comment))

    product_keywords = set(target_product.lower().split())
    partial_product = any(word in comment.lower() for word in product_keywords)
    
    # filtering logic
    # has product word + sentiment > 0.15 = passes check
    # has aspect word + sentiment > 0.15 = passes check
    # otherwise discard neutral non-meaningful comment
    if partial_product and abs(sentiment_score) > 0.15:
        return True
    elif has_aspect and abs(sentiment_score) > 0.15:
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        input_csv = pd.read_csv(input_file)
    except Exception as e:
        print(f"Could not read input file: {e}")

    # constructing output csv
    # clean comments and extract each comment aspects
    input_csv["cleaned_comment"] = input_csv["comment"].apply(clean_text)
    input_csv["aspects_found"] = input_csv["cleaned_comment"].apply(lambda x: find_aspects(x))

    # applying meaningful logic
    input_csv = input_csv[input_csv["cleaned_comment"].apply(lambda x: is_meaningful(x))]
    input_csv = input_csv[["video_id", "cleaned_comment", "aspects_found"]]

    # print(input_csv.head(10))

    input_csv.to_csv(output_file, index=False)
    print(f"Cleaned comments successfully saved.")