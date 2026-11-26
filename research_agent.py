import os
import re
import csv
import json
import asyncio
from pathlib import Path
from html.parser import HTMLParser
import httpx
from pydantic import BaseModel, Field
from typing import Literal, List
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.6-flash"
OUTPUT_JSON = Path("data.json")
OUTPUT_CSV = Path("data.csv")

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class VisibleTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: List[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head", "noscript", "svg"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head", "noscript", "svg"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def extract_visible_text(html: str, max_chars: int = 8000) -> str:
    parser = VisibleTextExtractor()
    parser.feed(html)
    cleaned = re.sub(r"\s+", " ", " ".join(parser.parts))
    return cleaned[:max_chars]


class AppResearchResult(BaseModel):
    id: int
    name: str
    category: str
    one_liner: str = Field(description="What the app does in one crisp sentence.")
    auth_methods: List[str] = Field(
        description="e.g., OAuth2, API Key, Bearer Token, Basic Auth, JWT, None/Local CLI"
    )
    access_gate: Literal[
        "Self-Serve (Free/Trial)",
        "Paid Plan Required",
        "Admin Approval Required",
        "Partner / Sales-Gated",
        "Open Source / Local",
    ]
    api_surface: str = Field(
        description="e.g., REST (Broad - 50+ endpoints), GraphQL, CLI/SDK only, Limited REST"
    )
    has_official_mcp: bool
    mcp_notes: str = Field(
        description="Details on official or community MCP availability"
    )
    buildable_today: Literal["Yes - Easy Win", "Yes - Moderate", "Blocked / Gated"]
    main_blocker: str = Field(
        description="None, or specific blocker like 'Enterprise sales gate', 'No public API', 'Strict app review'"
    )
    evidence_url: str = Field(
        description="Direct, publicly accessible HTTPS link to official developer docs or GitHub repo"
    )
    confidence_score: float = Field(description="0.0 to 1.0 confidence score")
    verification_status: str = "Unverified"


# Replace with your full list of 100 apps
APPS = [
    {"id": 1, "category": "CRM & Sales", "name": "Salesforce", "hint": "://salesforce.com"},
    {"id": 10, "category": "CRM & Sales", "name": "DealCloud", "hint": "dealcloud.com"},
    {"id": 58, "category": "Data, SEO & Scraping", "name": "Sherlock", "hint": "://github.com"},
    {"id": 91, "category": "AI, Research & Media", "name": "NotebookLM", "hint": "://google.com"},
]


async def call_gemini_with_retry(
    contents: str, config: types.GenerateContentConfig, retries: int = 4
):
    for attempt in range(retries):
        model_to_use = PRIMARY_MODEL if attempt < 2 else FALLBACK_MODEL
        try:
            return await client.aio.models.generate_content(
                model=model_to_use,
                contents=contents,
                config=config,
            )
        except APIError as e:
            if e.code in (429, 500, 503) and attempt < retries - 1:
                wait_time = (attempt + 1) * 3
                print(
                    f"  [!] {model_to_use} busy (HTTP {e.code}). Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            else:
                raise


async def pass_1_research(app: dict) -> dict:
    prompt = f"""
    Research the developer API and integration capabilities for:
    App: {app['name']} (ID: {app['id']}, Category: {app['category']}, Domain Hint: {app['hint']})
    
    Rules:
    - Be strictly factual. If an app requires talking to sales, enterprise licensing, or has no public API (like consumer NotebookLM vs Enterprise API, or CLI-only tools like Sherlock), state that accurately.
    - For evidence_url, provide a real, publicly reachable HTTPS URL to the official developer docs, product page, or GitHub repository.
    - Output exact id ({app['id']}), name ("{app['name']}"), and category ("{app['category']}").
    """

    config = types.GenerateContentConfig(
        system_instruction="You are a technical Product Ops researcher at Composio.",
        response_mime_type="application/json",
        response_schema=AppResearchResult,
        temperature=0.1,
    )

    response = await call_gemini_with_retry(prompt, config)
    result = AppResearchResult.model_validate_json(response.text)
    return result.model_dump()


async def fetch_page_text(http: httpx.AsyncClient, url: str) -> tuple[str | None, str | None]:
    """Fetches page text directly, falling back to Jina Reader if blocked (403) or JS-empty."""
    try:
        resp = await http.get(url)
        if resp.status_code == 200:
            text = extract_visible_text(resp.text, max_chars=8000)
            if len(text) >= 150:
                return text, None
        elif resp.status_code >= 400 and resp.status_code != 403:
            return None, f"Flagged (HTTP {resp.status_code})"
    except Exception:
        pass

    # Fallback: Jina Reader renders JS and bypasses basic WAF 403 blocks
    try:
        reader_resp = await http.get(f"https://jina.ai{url}", timeout=15.0)
        if reader_resp.status_code == 200 and len(reader_resp.text.strip()) >= 150:
            return reader_resp.text[:8000], None
        return None, f"Flagged (Unreachable / HTTP {reader_resp.status_code})"
    except Exception as e:
        return None, f"Flagged (Unreachable URL: {type(e).__name__})"


async def pass_2_verify_url(record: dict) -> dict:
    url = record["evidence_url"]
    if not url.startswith("http"):
        url = "https://" + url

    async with httpx.AsyncClient(
        follow_redirects=True, timeout=12.0, headers=BROWSER_HEADERS
    ) as http:
        visible_text, error_status = await fetch_page_text(http, url)

    if error_status:
        record["verification_status"] = error_status
        record["confidence_score"] = min(record["confidence_score"], 0.5)
        return record

    audit_prompt = f"""
    Verify these extracted claims against the visible page text from {url}:
    Claims: Auth={record['auth_methods']}, Gate={record['access_gate']}, API={record['api_surface']}
    Visible Page Text: {visible_text}
    
    Reply ONLY with 'VERIFIED' if the page text supports or aligns with the claims, or 'DISCREPANCY: <reason>' if clearly contradicted.
    """

    config = types.GenerateContentConfig(
        max_output_tokens=80,
        temperature=0.0,
    )

    audit = await call_gemini_with_retry(audit_prompt, config)
    record["verification_status"] = audit.text.strip()
    return record


def save_outputs(records: List[dict]):
    sorted_records = sorted(records, key=lambda x: x["id"])
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted_records, f, indent=2)

    if sorted_records:
        fieldnames = list(sorted_records[0].keys())
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in sorted_records:
                row_copy = row.copy()
                row_copy["auth_methods"] = ", ".join(row_copy["auth_methods"])
                writer.writerow(row_copy)


async def main():
    # Load existing progress if resuming an interrupted run
    completed_map = {}
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            for item in json.load(f):
                completed_map[item["id"]] = item

    pending_apps = [app for app in APPS if app["id"] not in completed_map]
    print(f"Loaded {len(completed_map)} completed apps. Running {len(pending_apps)} remaining...")

    sem = asyncio.Semaphore(4)
    lock = asyncio.Lock()

    async def process_app(app):
        async with sem:
            draft = await pass_1_research(app)
            verified = await pass_2_verify_url(draft)
            async with lock:
                completed_map[verified["id"]] = verified
                save_outputs(list(completed_map.values()))
            print(
                f"[{verified['id']}/100] {verified['name']} -> {verified['verification_status']}"
            )
            return verified

    await asyncio.gather(*(process_app(app) for app in pending_apps))
    print(f"Done! Saved {len(completed_map)} apps to {OUTPUT_JSON} and {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
