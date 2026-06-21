"""Debug script to check why job extraction is failing."""

import requests
import markdownify
from pathlib import Path

# Test a few career pages
test_urls = [
    ("Microsoft", "https://careers.microsoft.com/"),
    ("Google", "https://careers.google.com/"),
    ("IBM", "https://www.ibm.com/be-en/careers"),
    ("Salesforce", "https://www.salesforce.com/company/careers/"),
]

for name, url in test_urls:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print("="*60)

    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        html = resp.text

        md = markdownify.markdownify(html, strip=["script", "style", "head"])
        content_len = len(md.replace(" ", "").replace("\n", ""))

        print(f"HTML size: {len(html)} chars")
        print(f"Markdown size: {len(md)} chars")
        print(f"Content (no whitespace): {content_len} chars")
        print(f"Sparse detection threshold: 500 chars")

        if content_len < 500:
            print("STATUS: SPARSE - would retry with Playwright")
        else:
            print("STATUS: Content found - showing markdown preview...")
            # Show what's in the markdown
            lines = md.split("\n")
            print("\nFirst 30 lines of markdown:")
            for i, line in enumerate(lines[:30], 1):
                if line.strip():
                    print(f"  {line[:100]}")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
