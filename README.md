# SentiTech

SentiTech works as a multi-stage pipeline that turns raw product discussions into actionable insights. When a user searches for a product via the web interface, the system simultaneously searches YouTube for video transcripts and comments about the product, while querying tech discussion forums and review sites through Google. The collected data then flows through specialized preprocessing modules that clean, structure, and prepare the text for analysis — extracting sentences from forum posts, condensing transcripts to fit token limits, filtering comments for relevance and more.

Once the data is prepared, the system applies a complex AI analysis stack. Google ABSA (Aspect-Based Sentiment Analysis) breaks down forum discussions to identify specific product features and calculate sentiment scores for each aspect, YouTube EBSA (Emotion-Based Sentiment Analysis) runs a multi-layered emotion classification pipeline on relevant YouTube comments, while zero-shot classification processes video transcripts to categorize sentiment at the sentence level. Simultaneously, large language models generate high-level summaries, extract key benefits and drawbacks, and identify technical keywords that enthusiasts frequently mention. All these insights are then aggregated by the backend server, which orchestrates the entire pipeline, tracks progress in real-time, and serves the processed data to a React frontend that visualises everything from sentiment distributions and feature comparisons to emotion breakdowns and concise summaries.

---

## Screenshots

<img width="1920" height="1440" alt="details1_1" src="https://github.com/user-attachments/assets/913a18bf-54c0-474c-a5cb-c48f56e93033" />
<img width="1920" height="1440" alt="details1_2" src="https://github.com/user-attachments/assets/c54b0a46-9b23-4f16-83f1-8b263c7bf3bd" />
<img width="1920" height="1440" alt="details1_3" src="https://github.com/user-attachments/assets/b1585407-e6ca-42f7-8681-a81381485700" />
<img width="1920" height="1440" alt="details1_4" src="https://github.com/user-attachments/assets/748afd97-dd41-4cd4-af39-398972f7c61e" />
<img width="1920" height="1440" alt="details1_6" src="https://github.com/user-attachments/assets/6eae4c97-bf92-484b-a965-5041b12fc259" />

---

## Documentation

In this section I will briefly explain the file structure and what each file does.

The system is split into 5 distinct directories:

- **AI_Module**: where most of the backend AI processing takes place, including Google ABSA (Abstract Based Sentiment Analysis), YouTube EBSA (Emotion Based Sentiment Analysis), transcript zero-shot, LLM analysis, and more...
- **Backend_Module**: soley for the backend FastAPI server and relevant debugging files
- **Data_Collection**: directory for YouTube and Google data collection via web scraping and APIs
- **frontend-module**: directory dedicated to the react project for the frontend of the web app, hosted locally via node.js

Here is a brief file explaination for each directory, in the file structure order:

### AI Module
- **GetComparison.py**: calls perplexity API to retrieve comparison data and best feature data, then handles and structures output for backend server
- **GoogleABSA.py**: final pipeline stage for Google ABSA which holds aspect detection and aspect snippet sentiment calculation logic
- **progress_tracking.py**: helper file with one function to update the progress bar
- **snippets_log.py**: debug for GoogleABSA snippet calculations for tuning and tweaking
- **Summarization.py**: LLM summarization file, taking in 2 data points then summarising them through the LLM call and structuring the outputs, including watchdog for file change detection
- **tldr_output.log**: holds LLM output for TLDR feature used for debugging and instruction tweaking
- **TLDR-LLM.py**: TLDR (quick verdict) LLM file which takes in 3 data points, runs summarisation across multiple points and structures the output
- **TranscriptABSA.py**: zero-shot classification file which takes in transcript data and classifies aspect sentiments from each sentence
- **TranscriptLLM.py**: transcript LLM file which takes in shortened transcript data, and outputs summary points like benefits and drawbacks (and keyword cloud data)

### Backend Module
- **product_name.txt**: debugging step for safety, simply stores product name locally in a file as sometimes caching for product name was failing
- **main.py**: the main server python file holding the FastAPI functionality and all backend processing tasks
- **output.txt**: debugging step showing all the aspects and their respsective summaries for the frontend display in Google ABSA
- **output_prompt.txt**: debugging step showing the full backend AI prompt and aspect scores and aspect text blocks for summarisation
- **output_summaries.txt**: another debugging step also showing aspects and their summaries from processing feature sentiments
- **sentiment_debug.log**: generated hugging face debugging file for models
- **tldr_output.log**: TLDR (quick verdict) output file used for processing the model output
- **transcripts_distributions.json**: transcript distributions resulting from zero-shot classification

### Data Collection Module

#### Google Search Collection
- **ContextModelPrep.py**: final Google sentence pre-processing step for final sentence re-structuring, cleaning and preparing a dataset for the model in GoogleABSA
- **GoogleSearch.py**: script responsible for contacting Custom Search API to retrieve a list of discussion site links for processing
- **GoogleSearchCleaner.py**: structures the raw site data into sentences and does initial cleaning
- **GoogleSearchExtraction.py**: script using BeautifulSoup to extract all textual data from each site found from GoogleSearch.py
- **progress_tracking.py**: same progress update helper as before, used for updating progress for the progress bar
- **RunAll.py**: script which is called by the backend to run each Google pre-processing step sequentially in processes

#### YouTube Collection
- **CondenseTranscripts.py**: file for cleaning patterns and condensing the transcripts for token limits as LLM input to transcript LLM script
- **local_snippets_debug.txt**: debugging snippet file for YouTube ABSA from before (removed functionality)
- **PrepComments.py**: final comment processing step which carries out comment sentiment classification from pre-processed YouTube comments
- **PrepTranscripts.py**: transcript pre-processing step which splits transcripts into sentences and labels them with aspects for zero-shot ABSA script
- **progress_tracking.py**: same progress update helper as before, used for updating progress for the progress bar
- **RunAll.py**: script which is called by the backend to run each YouTube pre-processing step sequentially in processes
- **YouTubeSearch.py**: script responsible for calling the YouTube Data API to retrieve relevant videos, then retrieve comments / transcripts from those videos in a second call
- **YouTubeSearchCommentCleaner.py**: script that cleans and filters the YouTube comments in preperation for PrepComments.py

### Frontend Module

This module is a contained react project hosted locally with node. Most files are auto-generated when the project is initialized, but here are the main files to pay attention to:

**frontend-module -> src -> components**

This directory holds every React component that is rendered through App.js, corresponding to each seperate page or popup in the system:

- **ComparisonTool.js**: comparison tool page which builds the comparison table with the data from the backend
- **DataBreakdown.js**: data breakdown modal which is available on the FeatureSentiment page and EmotionInsights page via a button showing data statistics
- **EmotionInsights.js**: YouTube insights page (emotion insights), rendering comment examples, LLM transcript outputs, pie chart distributions and more
- **FeatureSentiment.js**: Google ABSA feature sentiment page holding the overall sentiment distribution, aspect distribution table and aspect mention frequencies 
- **GetStarted.js**: system welcome page showing a welcome box and product search box for the user to make a search
- **parseProducts.js**: AI generated helper for handling the AI generated auto-complete product list
- **Settings.js**: settings page which holds accessibility settings, toggles and language options for the user
- **Sidebar.js**: side navbar which is always visible in the system, only mode of navigation through all pages and holds paths to pages
- **Summarization.js**: summarization page, displaying high-level summarisations generated from the Summarization.py script

**frontend-module -> src -> App.js**

- Main react file responsible for rendering the main system components (core logic)

**frontend-module -> src -> styles**

This directory holds all of the styling for the react components:

- **comparison-tool.css**: comparison tool page css styling
- **data-breakdown.css**: data breakdown modal css styling
- **emotion-insights.css**: YouTube insights component css styling
- **feature-sentiment.css**: Google ABSA page css styling
- **get-started.css**: welcome page css styling
- **index.css**: main styling file linked through App.js
- **settings.css**: settings page css styling

**frontend-module -> src -> auto-complete.json**

- AI generated auto complete list used in parseProducts.js

### Inputs / Outputs Directory

This directory is self-explanatory and holds most of the input and output files which are produced by the data collection module and AI module. Once the system completes a full run, you can track each output here at each stage in the pipeline.

---

## How To Run The System

Here is a step-by-step guide on I (the developer) run the system locally, and how you can set it up locally aswell:

**Step One:** Open your code editor (I use VS Code)

**Step Two:** Load the project file into the code editor

**Step Three:** Make sure Python 3.10+ is installed, then run this command from the project root to install project dependencies:

```bash
pip install -r requirements.txt
```

**Step Four:** Install Node.js at: https://nodejs.org/en

**Step Five:** Terminal -> New Terminal (create a new terminal)

Run this command:
```bash
cd frontend-module
```

Then this command:
```bash
npm start
```

(The directory should be bsc-final/frontend-module and the second command should start the development server locally)  
(The react project should open in the browser on localhost:3000)

You should see something similar to this output in the terminal:

```
Compiled successfully!

You can now view frontend-module in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.0.111:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

**Step Six:** Terminal -> New Terminal (create a new terminal)

Run this command:
```bash
cd Backend_Module
```

Then this command:
```bash
uvicorn main:app --reload
```

(The directory should be bsc-final/Backend_Module and the second command should start the FastAPI server locally)

You should see something similar to this output in the second terminal:

```
INFO:     Will watch for changes in these directories: ['/Users/yarik/Documents/GitHub/bsc-final/Backend_Module']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [91400] using StatReload
INFO:     Started server process [91402]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Step Seven:** Read the full welcome box and use the system!

> **⚠️ PLEASE BEWARE BEFORE RUNNING!!**  
> Please beware that this system was developed locally on a powerful machine with 48GB of RAM and a 40-core GPU (utilised with MPS). Due to the sheer data volume and weight of the backend processing, processing speed will vary greatly and may put a large strain on your local resources.

If you would like to request a demo from me, please email me at: krasnovyasa@gmail.com, and i'll be more than happy to provide one.

> **Note:** This project is a refactored version with datasets and sensitive information removed. The `inputs-outputs` directory and `.env` file are excluded from version control for security and privacy.
