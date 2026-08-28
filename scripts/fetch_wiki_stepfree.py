import json
import re
import time

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (civic data project)"}
API = "https://en.wikipedia.org/w/api.php"

PAGES = {
    "Amersham Underground Station": "Amersham station",
    "Chalfont & Latimer Underground Station": "Chalfont & Latimer tube station",
    "Chesham Underground Station": "Chesham tube station",
    "Chorleywood Underground Station": "Chorleywood tube station",
    "Canning Town Underground Station": "Canning Town station",
    "Stratford Underground Station": "Stratford station",
    "West Ham Underground Station": "West Ham station",
    "Willesden Junction Underground Station": "Willesden Junction station",
}

out = {}
for our_name, wiki_title in PAGES.items():
    r = requests.get(API, headers=HEADERS, timeout=30, params={
        "action": "parse", "page": wiki_title, "prop": "wikitext",
        "format": "json", "redirects": 1,
    })
    r.raise_for_status()
    wikitext = r.json()["parse"]["wikitext"]["*"]
    hits = re.findall(r"(?i)step[ -_]?free access[^\n]{0,120}", wikitext)
    out[our_name] = hits
    print(f"\n== {our_name}")
    for h in hits[:4]:
        print("   ", " ".join(h.split())[:130])
    time.sleep(0.5)

with open("data/raw/wiki_stepfree_unknowns.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nwrote data/raw/wiki_stepfree_unknowns.json")
