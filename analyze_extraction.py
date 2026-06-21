"""Analyze current extraction performance and identify missed patterns."""

import requests
import markdownify
from src.jobscraper.ai_extractor import extract_jobs_from_markdown

# Test with a few companies that returned 0 jobs
test_cases = [
    ("Microsoft", "https://careers.microsoft.com/"),
    ("Google", "https://careers.google.com/"),
    ("Salesforce", "https://www.salesforce.com/company/careers/"),
]

print("="*70)
print("ANALYZING EXTRACTION PERFORMANCE")
print("="*70)

for company_name, url in test_cases:
    print(f"\n{company_name}")
    print("-" * 70)

    try:
        # Fetch and convert
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        html = resp.text

        # Try different markdown stripping options
        md_default = markdownify.markdownify(
            html, strip=["script", "style", "head"], heading_style="ATX"
        )
        md_minimal = markdownify.markdownify(
            html, strip=["script", "style"], heading_style="ATX"
        )

        print(f"HTML size: {len(html)} chars")
        print(f"Markdown (default strip): {len(md_default)} chars")
        print(f"Markdown (minimal strip): {len(md_minimal)} chars")

        # Look for job keywords in markdown
        keywords = [
            "job",
            "position",
            "role",
            "opening",
            "hiring",
            "apply",
            "apply now",
            "application",
            "careers",
            "title",
            "location",
            "salary",
        ]
        found = [k for k in keywords if k.lower() in md_default.lower()]
        print(f"Job keywords found: {found}")

        # Try extraction
        jobs = extract_jobs_from_markdown(
            md_default[:50_000], company_name, url
        )
        print(f"Jobs extracted: {len(jobs)}")

        # Show markdown preview (first meaningful content)
        lines = [
            l.strip()
            for l in md_default.split("\n")
            if l.strip() and len(l) > 20
        ]
        print(f"\nMarkdown preview (first 15 meaningful lines):")
        for line in lines[:15]:
            preview = line[:80].replace("\n", " ")
            print(f"  {preview}...")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
