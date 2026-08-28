import json
import pathlib
import time

import requests

BASE = "https://api.tfl.gov.uk"
HEADERS = {"User-Agent": "Mozilla/5.0"}
RAW = pathlib.Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

summary_path = RAW / "tube_stoppoints.json"
if not summary_path.exists():
    r = requests.get(f"{BASE}/StopPoint/Mode/tube", headers=HEADERS, timeout=30)
    r.raise_for_status()
    payload = r.json()
    print("total reported:", payload.get("total"), "| received:", len(payload["stopPoints"]))
    summary_path.write_text(json.dumps(payload))
stops = json.loads(summary_path.read_text())["stopPoints"]

print("summary mentions 'step':", "step" in json.dumps(stops).lower())

probe_ids = [stops[0]["id"]]
bank = [s for s in stops if s.get("naptanCode") or s.get("icsCode")][:0]
for s in stops:
    if s.get("commonName", "").startswith("Bank"):
        probe_ids.append(s["id"])
        break

for sid in probe_ids[:2]:
    r = requests.get(f"{BASE}/StopPoint/{sid}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    d = r.json()
    txt = json.dumps(d).lower()
    hits = [k for k in d.keys() if "step" in k.lower()]
    print(f"\n== {d.get('commonName')} ({sid}) keys={sorted(d.keys())}")
    print("direct step keys:", hits)
    for prop in d.get("additionalProperties") or []:
        name = str(prop.get("category", "")) + "/" + str(prop.get("name", ""))
        if "step" in name.lower() or "step" in str(prop.get("value", "")).lower():
            print("  prop:", name, "=", str(prop.get("value"))[:120])
    time.sleep(0.3)
