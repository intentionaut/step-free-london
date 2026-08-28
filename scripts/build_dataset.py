import json
import pathlib
import re

import pandas as pd

RAW = pathlib.Path("data/raw")
PROCESSED = pathlib.Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)


def normalize(name):
    n = str(name).lower()
    n = re.sub(r"\([^)]*\)", " ", n)
    n = re.sub(r"-\s*underground\s*$", " ", n)
    n = n.replace("&", " and ")
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    n = re.sub(r"\b(underground|international|london|tube)\b", " ", n)
    n = re.sub(r"\bstation\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


tfl = pd.read_csv(PROCESSED / "tube_stations_accessibility.csv")
print(f"tfl stations: {len(tfl)} | api lift status known: {tfl['access_via_lift'].notna().sum()}")

osm = json.loads((RAW / "osm_subway.json").read_text())["elements"]
osm_rows = []
for e in osm:
    tags = e.get("tags", {})
    osm_rows.append({
        "name_norm": normalize(tags.get("name", "")),
        "osm_name": tags.get("name"),
        "wheelchair": tags.get("wheelchair"),
    })
osm_df = pd.DataFrame(osm_rows).drop_duplicates(subset="name_norm")
print(f"osm stations: {len(osm_df)}")

dupes = osm_df["name_norm"].value_counts()
if (dupes > 1).any():
    print(dupes[dupes > 1])

tfl["name_norm"] = tfl["name"].map(normalize)
df = tfl.merge(osm_df, on="name_norm", how="left")
unmatched = df[df["osm_name"].isna()]["name"].tolist()
print(f"unmatched after join: {len(unmatched)} {unmatched[:10]}")


def final_flag(row):
    wc = row["wheelchair"]
    if wc == "yes":
        return "step-free"
    if wc == "limited":
        return "partial"
    if wc == "no":
        return "not step-free"
    return "unknown"


df["step_free"] = df.apply(final_flag, axis=1)
df["status_note"] = ""

overrides_path = RAW / "manual_overrides.csv"
if overrides_path.exists():
    overrides = pd.read_csv(overrides_path)
    for _, o in overrides.iterrows():
        mask = df["name"] == o["name"]
        if mask.any():
            df.loc[mask, ["step_free", "status_note", "wheelchair"]] = [
                o["step_free"], o["status_note"], "override"]
    print(f"applied {len(overrides)} manual overrides (see data/raw/manual_overrides.csv)")

both = df[df["access_via_lift"].notna() & df["wheelchair"].isin(["yes", "no"])].copy()
both["api_cat"] = both["access_via_lift"].str.lower().map({"yes": "yes", "no": "no"})
agree = (both["api_cat"] == both["wheelchair"]).sum()
print(f"\ncross-validation (API vs OSM, strict yes/no): {agree}/{len(both)} agree "
      f"({agree / len(both):.0%})")

disagreed = both[both["api_cat"] != both["wheelchair"]]
print(f"disagreements ({len(disagreed)}):")
for _, r in disagreed.iterrows():
    print(f"   {r['name']}: API={r['access_via_lift']} OSM={r['wheelchair']}")

partial_api_yes = df[(df["access_via_lift"] == "Yes") & (df["wheelchair"] == "limited")]
print(f"\nAPI 'Yes' that are OSM 'limited' (partial access): {len(partial_api_yes)}")

print("\nfinal step_free distribution:")
print(df["step_free"].value_counts())

out_cols = ["station_id", "name", "lat", "lon", "lines", "zone",
            "step_free", "wheelchair", "access_via_lift", "status_note",
            "access_notes", "source"]
df[out_cols].to_csv(PROCESSED / "tube_stepfree_final.csv", index=False)
print(f"\nwrote {PROCESSED / 'tube_stepfree_final.csv'}")
