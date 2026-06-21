"""Test if Playwright fallback works and renders jobs."""

import markdownify
from playwright.sync_api import sync_playwright

def test_playwright_render(url, company_name):
    """Test if Playwright can render a JS-heavy page and extract job content."""
    print(f"\n{'='*60}")
    print(f"Testing Playwright: {company_name}")
    print(f"URL: {url}")
    print("="*60)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            print("Loading page with Playwright...")
            page.goto(url, wait_until="networkidle", timeout=30_000)

            html = page.content()
            browser.close()

            print(f"HTML size: {len(html)} chars")

            md = markdownify.markdownify(html, strip=["script", "style", "head"])
            content_len = len(md.replace(" ", "").replace("\n", ""))

            print(f"Markdown size: {len(md)} chars")
            print(f"Content length: {content_len} chars")

            # Look for job-related keywords
            keywords = ["job", "position", "apply", "hiring", "role", "title", "location", "salary"]
            found_keywords = [k for k in keywords if k.lower() in md.lower()]

            print(f"Job keywords found: {found_keywords}")

            # Show preview
            lines = [l for l in md.split("\n") if l.strip() and len(l) > 20]
            print(f"\nFirst 20 non-empty lines:")
            for line in lines[:20]:
                print(f"  {line[:90]}")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

# Test a few major ATS systems
test_urls = [
    ("Microsoft", "https://careers.microsoft.com/"),
    ("Google", "https://careers.google.com/"),
]

for name, url in test_urls:
    test_playwright_render(url, name)
