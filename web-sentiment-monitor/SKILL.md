---
name: web-sentiment-monitor
description: "Performs 'Voice of the Customer' analysis by scraping the web for brand mentions, performing sentiment analysis, and generating an insight report with visualizations. Use this skill when asked to find out what people are saying about a company, product, or topic online, especially for marketing, brand, and product teams. It handles scraping news, blogs, and Reddit; analyzing sentiment; and creating charts."
---

# Web Sentiment Monitor

## Overview

This skill automates the process of gathering and analyzing online sentiment for a given search term. It follows a strict four-step process: Setup, Scrape, Analyze & Visualize, and Report.

## Workflow

### Step 1: Setup

1.  **Define Search Term:** Confirm the primary search term with the user (e.g., "Life360").
2.  **Define Workspace:** All temporary files will be stored in `/Users/john_renaldi/skills/.tmp/`. All final deliverables will be moved to `/Users/john_renaldi/skills/deliverables/`.

### Step 2: Scrape Web Content

1.  Use the `firecrawl_search` tool to find recent mentions of the search term. Execute two separate searches to gather a broad sample.
    *   **Search 1 (General Web/News):**
        ```json
        {
          "query": "SEARCH_TERM",
          "sources": [{"type": "web"}, {"type": "news"}],
          "limit": 15,
          "scrapeOptions": {
            "formats": ["markdown"]
          }
        }
        ```
    *   **Search 2 (Reddit):**
        ```json
        {
          "query": "site:reddit.com SEARCH_TERM",
          "sources": [{"type": "web"}],
          "limit": 15,
          "scrapeOptions": {
            "formats": ["markdown"]
          }
        }
        ```
2.  Combine the results from both searches into a single JSON array.
3.  Save the combined results to `/Users/john_renaldi/skills/.tmp/raw_mentions.json`.

### Step 3: Analyze & Visualize Data

This step uses the bundled Python script to process the scraped data.

1.  **Prepare Python Environment:** The script requires `pandas`, `matplotlib`, and `vaderSentiment`. Ensure they are installed in a virtual environment.
    *   Create venv: `python3 -m venv /Users/john_renaldi/skills/.tmp/venv`
    *   Install libs: `source /Users/john_renaldi/skills/.tmp/venv/bin/activate && pip install pandas matplotlib vaderSentiment`
2.  **Execute the Script:** Run the `process_and_visualize.py` script, providing the input file path and the output directory.
    *   `source /Users/john_renaldi/skills/.tmp/venv/bin/activate && python3 /Users/john_renaldi/skills/web-sentiment-monitor/scripts/process_and_visualize.py /Users/john_renaldi/skills/.tmp/raw_mentions.json /Users/john_renaldi/skills/.tmp/`
3.  **Verify Output:** The script will generate:
    *   `/Users/john_renaldi/skills/.tmp/analytical_summary.json`
    *   A `charts` directory: `/Users/john_renaldi/skills/.tmp/charts/` containing PNG images.

### Step 4: Assemble the Report

1.  Read the contents of `/Users/john_renaldi/skills/.tmp/analytical_summary.json`.
2.  Construct a final, human-readable report in Markdown format.
3.  The report **MUST** include:
    *   An **Executive Summary** section with the total mentions and average sentiment score.
    *   A **Sentiment & Source Breakdown** section that displays the `sentiment_distribution.png` and `source_breakdown.png` charts.
    *   A **Key Topics** section that displays the `top_topics.png` chart and discusses the main keywords.
    *   A **Noteworthy Mentions** section with a bulleted list of the top 5 most significant articles (from the `noteworthy_mentions` key in the JSON), including the title and a clickable link.
4.  Save the final report as `/Users/john_renaldi/skills/deliverables/sentiment_report.md`.
5.  Inform the user that the report and charts are complete and provide the path to the `deliverables` folder.
