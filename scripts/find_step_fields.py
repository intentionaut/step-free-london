import json
import pathlib

stops = json.loads(pathlib.Path("data/raw/tube_stoppoints.json").read_text())["stopPoints"]


def walk(node, path=""):
    hits = []
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else str(k)
            if "step" in str(k).lower() or "step" in str(v).lower()[:200]:
                hits.append((p, str(v)[:160]))
            hits += walk(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits += walk(v, f"{path}[{i}]")
    return hits


count = 0
for s in stops:
    hits = [h for h in walk(s) if "$type" not in h[0]]
    if hits:
        count += 1
        if count <= 6:
            print(f"\n== {s['commonName']} ({s['id']})")
            for p, v in hits[:8]:
                print("   ", p, "->", v)

print("\nstations mentioning 'step':", count, "/", len(stops))
