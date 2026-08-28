import json
import time

import requests

BASE = "https://api.tfl.gov.uk"
HEADERS = {"User-Agent": "Mozilla/5.0"}

for sid in ["940GZZLUKSX", "940GZZLUBOR"]:
    r = requests.get(f"{BASE}/StopPoint/{sid}", headers=HEADERS, timeout=30)
    d = r.json()
    print(f"\n===== {d['commonName']} ({sid})")
    props = d.get("additionalProperties") or []
    print(f"{len(props)} additionalProperties:")
    for p in props:
        v = str(p.get("value"))[:60].replace("\n", " ")
        print(f"   {json.dumps({k: p.get(k) for k in ('category', 'key', 'name', 'value')})}"
              .replace(str(p.get('value')), v))
    kids = d.get("children") or []
    print("children:", len(kids))
    for k in kids[:3]:
        print("   child:", k.get("commonName"), "| props:",
              [(p.get("category"), str(p.get("value"))[:40]) for p in (k.get("additionalProperties") or [])][:6])
    time.sleep(0.3)
