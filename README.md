# Step-Free London

A civic data story exploring where London's transport network leaves disabled
and older residents behind.

## The question

London prides itself on its public transport, but only a fraction of tube
stations are step-free. Where do disabled residents live relative to the
stations they can actually use — and which boroughs are worst served?

## Data sources (all free / open)

| Source | What we get | Where |
|---|---|---|
| TfL Unified API | Station locations, lines, zones (geometry is authoritative) | https://api.tfl.gov.uk |
| OpenStreetMap (Overpass API) | `wheelchair` tags — our primary step-free status layer | https://overpass-api.de |
| ONS Census 2021 (TS038) | Disabled residents per borough | https://www.ons.gov.uk/datasets/TS038 |
| TfL Step-free Tube guide (Apr 2026 PDF) | Authoritative per-station detail for manual overrides | https://content.tfl.gov.uk/step-free-tube-guide-map.pdf |
| ONS Census 2021 | Disability prevalence at LSOA level (next session) | https://www.ons.gov.uk |
| MHCLG IMD | Deprivation by neighbourhood (later) | via London Datastore |
| London Datastore | Borough boundaries (GeoJSON) | https://data.london.gov.uk |

## Findings so far (session 1)

- The TfL API's own `AccessViaLift` field exists for only 82 of 272 stations,
  and where it disagrees with OpenStreetMap (~31% of comparable stations),
  OSM is the more current one: Epping, High Barnet, Woodford and others got
  lifts years ago but still read "No" in the official API.
- Network-wide: **83 step-free / 26 partial / 152 not step-free / 8 untagged**.
- Full story + charts in `notebooks/01_fetch_stations.ipynb`; interactive map
  in `reports/step_free_london_map.html`.

## Findings: session 2 (lines & boroughs)

- Dataset completed: 87 step-free / 30 partial / 155 not — zero unknowns,
  every status carries a source note.
- **By line:** Jubilee is the most accessible (63% step-free, rebuilt for
  2000); Bakerloo is the worst (16%, opened 1906). Deep-level Victorian lines
  dominate the bottom of the chart.
- **By borough:** the naive hypothesis fails — correlation between a borough's
  % disabled residents and % inaccessible stations is r = 0.02. The gap is not
  where you'd guess from need alone.
- Worst combined gap: **Haringey** (13.7% disabled residents, only 1 of its 7
  stations fully accessible), Kensington & Chelsea (83% inaccessible),
  Camden, Westminster.
- Analysis in `notebooks/02_line_analysis.ipynb` and `notebooks/03_borough_gap.ipynb`.

## Approach

1. **Fetch** TfL station data incl. step-free status → `data/raw/`
2. **Map** step-free coverage per line and per area
3. **Join** Census disability prevalence + IMD to geography
4. **Compute** an "accessibility gap" score per borough
5. **Tell the story**: charts, maps, case studies → final report

## Structure

```
notebooks/       analysis notebooks (numbered in order)
scripts/         fetch + build pipeline (re-runnable, caches into data/raw)
reports/         generated maps and charts
data/raw/        downloaded data, never edited by hand
data/processed/  cleaned/joined datasets ready for plotting
```

## Setup

```bash
git clone https://github.com/intentionaut/step-free-london
cd step-free-london
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

## Stretch goals

- Add air quality (Breathe London / LAQN) — environment angle
- Proximity of LGBTQ+ venues to accessible stations
- Bus network as the accessibility fallback (buses are ramp-equipped)
