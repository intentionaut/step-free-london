import json
import pathlib
import time

import requests

BASE = "https://api.tfl.gov.uk"
HEADERS = {"User-Agent": "Mozilla/5.0"}
RAW = pathlib.Path("data/raw")

stops = json.loads((RAW / "tube_stoppoints.json").read_text())["stopPoints"]

borough_summary = next(s for s in stops if s["id"] == "4900ZZLUBOR1")
print("== summary props for", borough_summary["commonName"])
for p in borough_summary.get("additionalProperties") or []:
    print(f"   [{p.get('category')}] {p.get('name')} = {str(p.get('value'))[:80]}")

for sid in ["940GZZLUBOR", "940GZZLUKSX"]:
    r = requests.get(f"{BASE}/StopPoint/{sid}", headers=HEADERS, timeout=30)
    print(f"\n== detail {sid}: HTTP {r.status_code}")
    if r.ok:
        d = r.json()
        print("   top keys:", sorted(d.keys()))
        sf = {k: v for k, v in d.items() if "step" in k.lower()}
        print("   direct step fields:", sf)
        interesting = [
            p for p in d.get("additionalProperties") or []
            if "step" in str(p).lower()
        ]
        for p in interesting:
            print("   prop:", p.get("category"), "|", p.get("name"), "=", str(p.get("value"))[:100])
        kids = d.get("children") or []
        kid_hits = [k.get("commonName") for k in kids if "step" in json.dumps(k).lower()]
        print("   children mentioning step:", kid_hits[:5])
    time.sleep(0.3)
