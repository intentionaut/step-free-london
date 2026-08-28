import re

import pdfplumber

UNKNOWN = [
    "Amersham",
    "Chalfont & Latimer",
    "Chesham",
    "Chorleywood",
    "Canning Town",
    "Stratford",
    "West Ham",
    "Willesden Junction",
]

pages = []
with pdfplumber.open("data/raw/step-free-tube-guide-map.pdf") as pdf:
    print(f"pages: {len(pdf.pages)}")
    for p in pdf.pages:
        text = p.extract_text() or ""
        pages.append(text)

full = "\n".join(pages)
print(f"extracted {len(full)} chars")

for station in UNKNOWN:
    idxs = [m.start() for m in re.finditer(re.escape(station), full)]
    if not idxs:
        print(f"\n=== {station}: NOT FOUND")
        continue
    for i in idxs[:2]:
        snippet = " ".join(full[i:i + 260].split())
        print(f"\n=== {station}: ...{snippet}...")
