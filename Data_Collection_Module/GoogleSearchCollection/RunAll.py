import os
import sys
import subprocess
from progress_tracking import update_progress

script_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No product name given.")
        sys.exit(1)
    
    product_name = sys.argv[1]

    # run GoogleSearch.py with product name
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/GoogleSearchCollection/GoogleSearch.py"), product_name])
    update_progress("google", 20)

    # run the rest of pipeline
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/GoogleSearchCollection/GoogleSearchExtraction.py")])
    update_progress("google", 20)
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/GoogleSearchCollection/GoogleSearchCleaner.py")])
    update_progress("google", 20)
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/GoogleSearchCollection/ContextModelPrep.py")])
    update_progress("google", 20)
    subprocess.run(["python3", os.path.join(script_dir, "../../AI_Module/GoogleABSA.py"), product_name])
    update_progress("google", 20)
