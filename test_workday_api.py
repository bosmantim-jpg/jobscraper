"""Test Workday API with Intel."""

from src.jobscraper.ats_fetcher import detect_and_fetch_from_ats

# Test with Intel (Workday)
intel_url = "https://intel.wd1.myworkdayjobs.com/en-US/External?shared_id=NTA3OGJmNzQtNjNiOS00MWYyLWJlNDItYjdhMDAyM2I2OWVh"

print("Testing Workday API with Intel")
print("="*60)
print(f"URL: {intel_url[:80]}...")

jobs = detect_and_fetch_from_ats(intel_url)

if jobs is not None:
    print(f"\nSuccess! Fetched {len(jobs)} jobs via Workday API")
    if len(jobs) > 0:
        print("\nFirst 3 jobs:")
        for job in jobs[:3]:
            print(f"  - {job.get('title', 'N/A')}")
            print(f"    Location: {job.get('location', 'N/A')}")
else:
    print("\nNo jobs found or API unavailable")
