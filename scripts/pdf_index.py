import re

import pdfplumber

TARGETS = ["Amersham", "Chalfont", "Chesham", "Chorleywood",
           "Canning Town", "Stratford", "West Ham", "Willesden"]

with pdfplumber.open("data/raw/step-free-tube-guide-map.pdf") as pdf:
    page = pdf.pages[1]
    words = page.extract_words(x_tolerance=1.5, y_tolerance=2)

rows = {}
for w in words:
    key = round(w["top"] / 3) * 3
    rows.setdefault(key, []).append(w)

lines = []
for key in sorted(rows):
    ws = sorted(rows[key], key=lambda w: w["x0"])
    lines.append((key, " ".join(x["text"] for x in ws)))

print(f"{len(lines)} reconstructed lines")

for target in TARGETS:
    found = False
    for key, text in lines:
        if target.lower() in text.lower():
            print(f"\n[{target}] {text[:200]}")
            found = True
            break
    if not found:
        partial = [t for _, t in lines if target.split()[0].lower() in t.lower()]
        print(f"\n[{target}] exact row miss; candidates: {partial[:2]}")
