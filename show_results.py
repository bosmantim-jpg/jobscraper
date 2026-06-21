"""Display scrape results comparison."""

import json
from pathlib import Path

print("="*70)
print("SCRAPE RESULTS WITH ATS API INTEGRATION")
print("="*70)

with open("jobs_db.json") as f:
    db = json.load(f)

job_count = len(db)
print(f"\nTotal jobs found: {job_count}")

# Compare with backup
try:
    with open("jobs_db.json.backup") as f:
        backup = json.load(f)
    backup_count = len(backup)
    diff = job_count - backup_count
    pct = round((diff / backup_count) * 100, 1) if backup_count > 0 else 0

    print(f"\nComparison with previous run:")
    print(f"  Previous run: {backup_count} jobs")
    print(f"  Current run:  {job_count} jobs")
    if diff > 0:
        print(f"  Change: +{diff} jobs ({pct}% increase)")
    elif diff < 0:
        print(f"  Change: {diff} jobs ({pct}% decrease)")
    else:
        print(f"  Change: No change")
except FileNotFoundError:
    pass

# Jobs by status
print(f"\nJobs by status:")
status_counts = {}
for job in db.values():
    status = job.get("status", "unknown")
    status_counts[status] = status_counts.get(status, 0) + 1

for status in sorted(status_counts.keys()):
    print(f"  {status}: {status_counts[status]}")

# Top companies
print(f"\nTop 10 companies by job count:")
company_counts = {}
for job in db.values():
    company = job.get("company", "unknown")
    company_counts[company] = company_counts.get(company, 0) + 1

for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {company}: {count} jobs")

# Extraction methods
print(f"\nExtraction methods used:")
output_file = Path(
    "C:/Users/TIM~1.BOS/AppData/Local/Temp/claude/C--timprojects-jobscraper/8f99508a-792a-445d-a1ad-de4cfa1a2701/tasks/bv85po5a2.output"
)
if output_file.exists():
    with open(output_file) as f:
        lines = f.readlines()
        ats_count = len([l for l in lines if "ATS API" in l])
        html_count = len([l for l in lines if "HTML + AI" in l])
        print(f"  ATS API used: {ats_count} times")
        print(f"  HTML + AI used: {html_count} times")

# Sample jobs
print(f"\nSample jobs found:")
for i, (job_id, job) in enumerate(list(db.items())[:5]):
    print(f"  - {job.get('title')} @ {job.get('company')} ({job.get('location', 'N/A')})")

print(f"\n✓ Full export: output/jobs_2026-06-21.xlsx")
