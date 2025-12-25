import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file = os.path.join(script_dir, "../inputs-outputs/progress.json")

def update_progress(module, percent):
    with open(progress_file, "r") as f:
        progress_data = json.load(f)

    progress_data[module] += percent

    if all(isinstance(v, int) and v == 100 for k, v in progress_data.items() if k != "completed"):
        progress_data["completed"] = True

    with open(progress_file, "w") as f:
        json.dump(progress_data, f)