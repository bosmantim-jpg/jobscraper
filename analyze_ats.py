"""Analyze companies.xlsx to identify ATS types."""

import pandas as pd

df = pd.read_excel('companies.xlsx')

print("Companies by ATS Type\n" + "="*60)

for ats, pattern in [
    ('greenhouse', 'greenhouse'),
    ('lever', 'lever'),
    ('workday', 'myworkday|workday'),
    ('custom', None),
]:
    if pattern:
        mask = df['Job / Career Pagina'].str.contains(pattern, case=False, na=False)
    else:
        # Everything else
        mask = ~(
            df['Job / Career Pagina'].str.contains(
                'greenhouse|lever|myworkday|workday', case=False, na=False
            )
        )

    matching = df[mask]
    if len(matching) > 0:
        print(f"\n{ats.upper()}: {len(matching)} companies")
        for idx, row in matching.head(5).iterrows():
            url = row['Job / Career Pagina']
            print(f"  - {row['Company']}: {url[:70]}...")
        if len(matching) > 5:
            print(f"  ... and {len(matching)-5} more")
