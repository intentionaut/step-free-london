import json
import pathlib
import re
import time

import pandas as pd
import requests

BASE = "https://api.tfl.gov.uk"
HEADERS = {"User-Agent": "Mozilla/5.0"}
RAW = pathlib.Path("data/raw")
DETAIL_DIR = RAW / "station_details"
DETAIL_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED = pathlib.Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)


def normalize(name):
    n = str(name).lower()
    n = n.replace("&", " and ")
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    n = re.sub(r"\b(underground|international)\b", " ", n)
    n = re.sub(r"\bstation\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def fetch_json(url):
    for attempt in range(6):
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", 15 * (attempt + 1)))
            print(f"   429 rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"gave up on {url}")


def props_to_record(s):
    rec = {
        "access_via_lift": None,
        "access_notes": None,
        "zone": None,
    }
    for p in s.get("additionalProperties") or []:
        key = p.get("key")
        val = p.get("value")
        if key == "AccessViaLift":
            rec["access_via_lift"] = str(val).strip().capitalize()
        elif key == "AddtionalInformation":
            rec["access_notes"] = (val or "").strip() or None
        elif key == "Zone":
            rec["zone"] = str(val).strip()
    return rec


stops = json.loads((RAW / "tube_stoppoints.json").read_text())["stopPoints"]

name_lookup = {}
conflicts = set()
for s in stops:
    rec = props_to_record(s)
    if rec["access_via_lift"] is None:
        continue
    key = normalize(s.get("commonName"))
    prev = name_lookup.get(key)
    if prev and prev["access_via_lift"] != rec["access_via_lift"]:
        conflicts.add(key)
    elif prev is None or (rec["access_notes"] and not prev["access_notes"]):
        name_lookup[key] = rec

print(f"name lookup entries: {len(name_lookup)} | conflicting names: {len(conflicts)}")

stations = [
    s for s in stops
    if "tube" in s.get("modes", []) and str(s.get("id", "")).startswith("940GZZ")
]
print(f"canonical tube stations: {len(stations)}")

records = []
to_fetch = []
for s in stations:
    rec = props_to_record(s)
    row = {
        "station_id": s["id"],
        "name": s.get("commonName", "").strip(),
        "lat": s.get("lat"),
        "lon": s.get("lon"),
        "lines": ", ".join(sorted({l["name"] for l in s.get("lines") or []})),
        **rec,
        "source": "summary",
    }
    key = normalize(row["name"])
    if row["access_via_lift"] is None and key not in conflicts and key in name_lookup:
        fill = name_lookup[key]
        row.update({
            "access_via_lift": fill["access_via_lift"],
            "access_notes": fill["access_notes"] or row["access_notes"],
            "zone": row["zone"] or fill["zone"],
            "source": "sibling",
        })
    if row["access_via_lift"] is None:
        to_fetch.append((s["id"], row))
    records.append(row)

print(f"need detail fetch: {len(to_fetch)}")

for sid, row in to_fetch:
    cache = DETAIL_DIR / f"{sid}.json"
    if not cache.exists():
        print(f"   fetching {row['name']} ({sid})")
        cache.write_text(json.dumps(fetch_json(f"{BASE}/StopPoint/{sid}")))
        time.sleep(1.2)
    rec = props_to_record(json.loads(cache.read_text()))
    row.update({
        **rec,
        "zone": row["zone"] or rec["zone"],
        "source": "detail",
    })

df = pd.DataFrame(records)
df.loc[df["access_notes"].notna() & (df["source"] == "summary"), "source"] = df["source"]

still_missing = df[df["access_via_lift"].isna()]
print(f"\nfinal coverage: {df['access_via_lift'].notna().sum()}/{len(df)}")
if len(still_missing):
    print("unknown:", still_missing["name"].tolist())

print("\nAccessViaLift distribution:")
print(df["access_via_lift"].value_counts(dropna=False))

out = PROCESSED / "tube_stations_accessibility.csv"
df.to_csv(out, index=False)
print(f"\nwrote {out}")
