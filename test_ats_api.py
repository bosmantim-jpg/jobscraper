"""Test ATS API fetching."""

from src.jobscraper.ats_fetcher import detect_and_fetch_from_ats

# Test URLs - these should work if the companies use these ATS systems
test_cases = [
    # Greenhouse examples
    (
        "Greenhouse Example",
        "https://boards.greenhouse.io/api/v1/boards/example/jobs",
    ),
    # Lever examples
    ("Lever Example", "https://example.lever.co/jobs"),
    # Workday examples
    (
        "Workday Example",
        "https://example.wd5.myworkdayjobs.com/en-US/External",
    ),
]

print("Testing ATS API Fetchers\n" + "=" * 60)

for name, url in test_cases:
    print(f"\nTest: {name}")
    print(f"URL: {url}")

    jobs = detect_and_fetch_from_ats(url)

    if jobs is None:
        print("Result: No ATS API detected (would fall back to HTML)")
    elif isinstance(jobs, list):
        print(f"Result: {len(jobs)} jobs fetched via ATS API")
        for job in jobs[:2]:
            print(f"  - {job.get('title', 'N/A')} @ {job.get('location', 'N/A')}")
    else:
        print(f"Result: Unexpected response type: {type(jobs)}")

print("\n" + "=" * 60)
print("Testing real company URL")

# Test with a real Greenhouse company (if available)
real_url = "https://boards.greenhouse.io/api/v1/boards/uber/jobs"
print(f"\nTest: Real Greenhouse URL (Uber)")
print(f"URL: {real_url}")

jobs = detect_and_fetch_from_ats(real_url)
if jobs:
    print(f"Success! Found {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"  - {job.get('title')} ({job.get('location')})")
else:
    print("Could not fetch (API may be unavailable or company not found)")
