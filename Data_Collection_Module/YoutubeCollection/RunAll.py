from concurrent.futures import ThreadPoolExecutor
import os
import sys
import subprocess

from progress_tracking import update_progress

script_dir = os.path.dirname(os.path.abspath(__file__))

def run_comments(product_name):
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/YoutubeCollection/YoutubeSearchCommentCleaner.py"), product_name])
    update_progress("youtube", 15)
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/YoutubeCollection/PrepComments.py")])
    update_progress("youtube", 15)

def run_transcripts():
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/YoutubeCollection/PrepTranscripts.py")])
    update_progress("youtube", 15)
    subprocess.run(["python3", os.path.join(script_dir, "../../AI_Module/TranscriptABSA.py")])
    update_progress("youtube", 15)

def run_LLM(product_name):
    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/YoutubeCollection/CondenseTranscripts.py")])
    update_progress("youtube", 15)
    subprocess.run(["python3", os.path.join(script_dir, "../../AI_Module/TranscriptLLM.py"), product_name])
    update_progress("youtube", 15)

# changed to processes running in parralel like backend, speed improvements
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No product name given.")
        sys.exit(1)
    
    product_name = sys.argv[1]

    subprocess.run(["python3", os.path.join(script_dir, "../../Data_Collection_Module/YoutubeCollection/YoutubeSearch.py"), product_name])
    update_progress("youtube", 10)

    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(run_comments, product_name)
        future2 = executor.submit(run_transcripts)
        future3 = executor.submit(run_LLM, product_name)

        future1.result()
        future2.result()
        future3.result()
