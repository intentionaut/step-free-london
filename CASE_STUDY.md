# Step-Free London: a case study in civic data

The full methodology, findings and the outcomes we hope data like this can reach.
This document backs the analysis in `notebooks/`, and the code in `scripts/`
re-runs every number below.

---

## The question

London prides itself on its public transport, and with reason: it has one of
the most complete urban rail networks in the world. But ambition is not
coverage. Only a fraction of tube stations are step-free, and that fraction
decides who the network is actually for.

So the project set out to answer one plain question properly: **where do
disabled residents live relative to the stations they can actually use, and
which boroughs are worst served?**

Nothing in this question is a mystery to the people it affects. A wheelchair
user living near a non-step-free station does not need a dataset to know their
neighbourhood is poorly served. The point of gathering the data is different. It
is to move the conversation from anecdote to argument, from "someone should do
something" to a named, numbered, rankable list of where the gap is worst and by
how much.

When something works beautifully for the people it was built around and poorly
for everyone else, that is rarely an accident and rarely an edge case. It is a
decision, whether anyone meant it to be or not. Step-free London is an attempt
to measure those decisions.

## Methodology

Five sources, all free and open. Each plays a distinct role, and the most useful
methodological choices were about *trusting the sources against each other*,
not about which source is biggest.

| Layer | Source | What it provides | Why it's there |
|---|---|---|---|
| Geometry | TfL Unified API | Station points, lines, zones | Authoritative locations, but its access field is unreliable |
| Crowdsourced truth | OpenStreetMap (Overpass) | `wheelchair` tags | The *primary* step-free status layer |
| Need | ONS Census 2021 (TS038) | Disabled residents per borough | Demand side of the gap |
| Final word | TfL Step-free Guide (Apr 2026 PDF) | Per-station manual detail | Authoritative override layer |
| Boundaries | London Datastore | Borough GeoJSON | Keeps the geography honest |

The pipeline runs in four stages (`scripts/`):

1. **Fetch.** Pull stations from the TfL API and `wheelchair` tags from
   Overpass; cache everything into `data/raw/` untouched.
2. **Cross-check.** Every station's status is defined by its OSM tag, then
   checked against the TfL API's `AccessViaLift` field and the official PDF
   guide. Where they disagree, the manual override wins and is recorded.
3. **Join.** Attach Census disability prevalence at borough level and
   boundaries, so coverage can be viewed against need.
4. **Score.** Compute a per-borough accessibility gap. The final dataset
   carries each station's status *and a source note for that status*, so every
   claim can be checked and re-run.

Two decisions made the findings trustworthy.

**We did not trust the official API's access field as ground truth.** The TfL
API records `AccessViaLift` for only 82 of 272 stations. Where the API and
OpenStreetMap disagreed on a comparable station (about 31% of them), OSM was
consistently the more current source. Epping, High Barnet and Woodford all
gained lifts years ago and still read "No" in the official interface. The
official record of the network had fallen behind the network itself.

**We committed to zero unknowns.** Session one finished with 8 of 272 stations
untagged. Session two closed every one, and every status now carries a source
note. A dataset with blanks is a dataset with opinions in it: whoever fills the
blanks later decides the answer. Specifying every status, even at the cost of
some manual work against a PDF, makes the dataset honest.

## What we found

- **The network is not for everyone.** Of 272 stations, 87 are
  fully step-free, 30 partially, and 155 not at all. Roughly a third of it is
  fully usable. You would not guess that from how London talks about its
  transport.
- **The lines tell the history.** The Jubilee line is the most accessible
  (63% step-free, rebuilt for 2000). The Bakerloo is the worst (16%, opened
  1906). The bottom of the chart is dominated by deep-level Victorian lines.
  The accessibility of the network is a fossil record of when each line was
  built, and who was imagined standing at its stations.
- **The naive hypothesis fails, cleanly.** Common sense says the boroughs with
  the most disabled residents would be the worst served. The correlation between
  a borough's percentage of disabled residents and its percentage of
  inaccessible stations is r = 0.02. There is no relationship at all. The gap is
  not where you would guess from need alone. It tracks wealth, history and
  lobbying power far more than it tracks demand.
- **The worst places are now named.** Haringey has 13.7% disabled residents and
  only one of its seven stations fully accessible. Kensington & Chelsea has 83%
  of its stations inaccessible. Camden and Westminster sit on the same list. The
  dataset converts "the worst served boroughs" from a vague feeling into a
  ranked list with receipts.

You can sit in the data yourself: `notebooks/` walks through the analysis, and
the live map at the project site plots every station.

## Outcomes we might hope for

Data gathered this way is worth little until it moves someone. Here are the
outcomes we hope for, in rough order of how likely they are:

1. **The official data gets corrected.** TfL's own API field is stale. A
   reproducible public comparison of API versus ground truth is the cheapest,
   most defensible pressure a citizen can apply to a data owner. Updating one
   field in one API feels small, but it changes what every future analysis
   built on that API concludes.
2. **Advocacy gets targets.** Transport for All, borough accessibility groups
   and disability organisations can now say "Haringey, first, because the gap
   is biggest relative to need" instead of gesturing at the problem generally.
   Named, ranked, reproducible gaps are ammunition.
3. **A story gets told.** Media and campaigners can point at the newsworthiness
   that fell out of the hypothesis failing: the need gap and the accessibility
   gap barely correlate, which means the network's shape reflects decisions, not
   demand. That is a claim a journalist can check, and a claim that opens doors
   (and station barriers).
4. **Future plans get a baseline.** Any borough-level scheme, from new lift
   funding to accessible transport plans, can be checked against this dataset
   rather than assumptions. Today it measures the gap; tomorrow it measures
   whether the gap closed.
5. **The method outlives this project.** The cross-check-against-ground-truth,
   zero-unknowns, source-noted approach transfers directly to product and data
   work: the vendor field you trust is probably stale, the follow-up question is
   always "is this data true *right now*", and blanks are claims in disguise.

## What this teaches about gathering this kind of data

- **Official does not mean current.** Any dataset that records a physical world
   drifts. Budget for a ground-truth cross-check, or your analysis goes stale
   with it.
- **Hypotheses are cheap, and so is being wrong.** The r = 0.02 result is the
   most valuable output of the whole project, more valuable than any chart. A
   project that only confirms what it expected had found nothing. Strong
   opinions are useful; being useful means recording when the data disagrees.
- **Completeness is a political act.** Leaving 8 stations untagged would have
   let the answer depend on whoever got there last. Closing every unknown makes
   the dataset say something, and say it audibly.
- **Accessibility data is a decision ledger.** "Not step-free" is not a
   technical fact about a Victorian tunnel. It is a decision about who the
   station is for. Data like this is one of the only ways a citizen can see, let
   alone argue with, those decisions at the scale of a whole city.

---

*Reproduce everything:* `git clone https://github.com/intentionaut/step-free-london`,
install `requirements.txt`, run the scripts in number order, and read the numbers
back into the notebooks.