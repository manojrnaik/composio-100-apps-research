composio-100-apps-research

# B2B SaaS & AI Software Research Agent

An asynchronous Python research pipeline powered by Google Gemini (`google-genai`) that researches software applications across categories (CRM, AI, Data & Scraping, etc.), extracts structured insights, exports datasets to JSON and CSV, and generates Markdown summaries alongside an interactive HTML dashboard.

## ?? Overview

This tool automates software discovery and competitive research from a target list (`apps.json`). Using asynchronous HTTP requests (`httpx`), HTML parsing, and structured LLM outputs (`pydantic` + `google-genai`), it collects categorized application intelligence and compiles it into both `REPORT.md` and `dashboard.html`.

## ?? Repository Structure

```text
+-- .gitignore           # Specifies intentionally untracked files (e.g., .env)
+-- README.md            # Project documentation
+-- REPORT.md            # Auto-generated Markdown summary report
+-- apps.json            # Input configuration with target apps, categories, and domain hints
+-- dashboard.html       # Auto-generated interactive HTML dashboard
+-- data.csv             # Collected dataset in tabular CSV format
+-- data.json            # Collected dataset in raw JSON format
+-- generate_report.py   # Compiles data.json into REPORT.md and dashboard.html
+-- requirements.txt     # Python package dependencies
+-- research_agent.py    # Async research agent using Gemini, httpx, and Pydantic
```

## ?? Getting Started

### Prerequisites

* **Python 3.9+**
* A **Google Gemini API Key**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manojrnaik/composio-100-apps-research.git
   cd your-repo-name
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## ?? Usage

1. **Configure Target Applications:**
   Add or edit entries in `apps.json`.

2. **Run the Research Agent:**
   Fetch and structure application data into `data.json` and `data.csv`:
   ```bash
   python research_agent.py
   ```

3. **Generate Reports & Dashboard:**
   Build `REPORT.md` and `dashboard.html` from the collected data:
   ```bash
   python generate_report.py
   ```

4. **View Outputs:**
   * Open `REPORT.md` in any Markdown viewer for the categorized summary.
   * Open `dashboard.html` in your web browser to explore the interactive dashboard.

## ?? Input Format (`apps.json`)

Each entry in `apps.json` defines a target application with a unique ID, category, name, and domain hint:

```json
[
  {
    "id": 1,
    "category": "CRM & Sales",
    "name": "Salesforce",
    "hint": "://salesforce.com"
  },
  {
    "id": 10,
    "category": "CRM & Sales",
    "name": "DealCloud",
    "hint": "dealcloud.com"
  },
  {
    "id": 58,
    "category": "Data, SEO & Scraping",
    "name": "Sherlock",
    "hint": "://github.com"
  },
  {
    "id": 91,
    "category": "AI, Research & Media",
    "name": "NotebookLM",
    "hint": "://google.com"
  }
]
```

### Field Descriptions
* **`id`**: Unique numeric identifier for the application.
* **`category`**: Industry or functional grouping used for report aggregation.
* **`name`**: Name of the software or tool to research.
* **`hint`**: Domain or URL clue to guide web resolution and disambiguation.

