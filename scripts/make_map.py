import pathlib

import folium
import pandas as pd

df = pd.read_csv("data/processed/tube_stepfree_final.csv")

colors = {
    "step-free": "#2e7d32",
    "partial": "#f9a825",
    "not step-free": "#c62828",
    "unknown": "#9e9e9e",
}

m = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles="CartoDB positron")

for _, r in df.iterrows():
    flag = r["step_free"]
    popup = (
        f"<b>{r['name']}</b><br>"
        f"Lines: {r['lines']}<br>"
        f"Status: {flag}<br>"
        f"OSM wheelchair: {r['wheelchair'] or 'untagged'}<br>"
        f"TfL API lift: {r['access_via_lift'] or 'not recorded'}"
    )
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=5,
        color=colors[flag],
        fill=True,
        fill_opacity=0.85,
        weight=1,
        popup=folium.Popup(popup, max_width=260),
    ).add_to(m)

title = (
    "<h3 style='text-align:center;margin:6px'>Step-Free London: tube station "
    "wheelchair access</h3>"
    "<p style='text-align:center;margin:2px'>Access status from OpenStreetMap, "
    "cross-checked against the TfL Unified API</p>"
)
m.get_root().html.add_child(folium.Element(title))

out = pathlib.Path("reports")
out.mkdir(exist_ok=True)
path = out / "step_free_london_map.html"
m.save(path)
print(f"wrote {path}")
print(df["step_free"].value_counts().to_string())
