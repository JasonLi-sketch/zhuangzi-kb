#!/usr/bin/env python3
"""Merge all Zhuangzi allegory events and extract concept relations."""
import json
import os
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. Merge all events ────────────────────────────────────────────────
events_dir = os.path.join(BASE, "data", "events")
event_files = sorted(glob.glob(os.path.join(events_dir, "Z*.json")))

all_events = []
all_relations = []

for ef in event_files:
    with open(ef) as f:
        event = json.load(f)
    all_events.append(event)
    
    # Extract relations from event
    if "concept_relations" in event:
        for rel in event["concept_relations"]:
            rel_copy = dict(rel)
            rel_copy["event_id"] = event["event_id"]
            all_relations.append(rel_copy)

# Sort events by event_id
all_events.sort(key=lambda e: e["event_id"])

# Write merged events
events_out = os.path.join(BASE, "data", "dialogue_events.json")
with open(events_out, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)
print(f"Merged {len(all_events)} events -> dialogue_events.json")

# Write relations
relations_out = os.path.join(BASE, "data", "concept_relations.json")
with open(relations_out, "w", encoding="utf-8") as f:
    json.dump(all_relations, f, ensure_ascii=False, indent=2)
print(f"Extracted {len(all_relations)} relations -> concept_relations.json")

# Summary by chapter
chapter_counts = {}
for e in all_events:
    ch = e.get("chapter", "unknown")
    chapter_counts[ch] = chapter_counts.get(ch, 0) + 1
print(f"\nEvents by chapter:")
for ch, cnt in sorted(chapter_counts.items()):
    print(f"  {ch}: {cnt} events")

# ── 2. Generate Graph ──────────────────────────────────────────────────
nodes = set()
edges = []

for rel in all_relations:
    src = rel["source"]
    tgt = rel["target"]
    rtype = rel["type"]
    nodes.add(src)
    nodes.add(tgt)
    edges.append((src, tgt, rtype))

# Also add concept markers as nodes
for e in all_events:
    for c in e.get("key_concepts", []):
        nodes.add(c["marker"])

# Build DOT
dot_lines = ['digraph ZhuangziKnowledgeGraph {']
dot_lines.append('  rankdir=LR;')
dot_lines.append('  graph [fontname="Noto Sans CJK SC" dpi=150];')
dot_lines.append('  node [fontname="Noto Sans CJK SC" shape=box style=rounded];')
dot_lines.append('  edge [fontname="Noto Sans CJK SC"];')

# Add nodes
for n in sorted(nodes):
    label = n.replace("\u301c", "").replace("\u301d", "")
    if n.startswith("\u301c") and n.endswith("\u301d"):
        dot_lines.append(f'  "{n}" [label="{label}" style="filled,rounded" fillcolor="#FFF4E0"];')
    elif n.startswith("Z0"):
        dot_lines.append(f'  "{n}" [label="{n}" style="filled,rounded" fillcolor="#E8F4FD"];')
    else:
        dot_lines.append(f'  "{n}" [label="{label}" style="filled,rounded" fillcolor="#F0F0F0"];')

# Add edges
edge_colors = {
    "体用关系": "#E74C3C",
    "同一关系": "#2ECC71",
    "工夫关系": "#3498DB",
    "寓言关系": "#9B59B6",
    "对反关系": "#E67E22",
    "条件关系": "#1ABC9C",
    "推导关系": "#95A5A6",
    "示例关系": "#F39C12"
}

for src, tgt, rtype in edges:
    color = edge_colors.get(rtype, "#7F8C8D")
    dot_lines.append(f'  "{src}" -> "{tgt}" [label="{rtype}" color="{color}" fontsize=9];')

dot_lines.append('}')

dot_out = os.path.join(BASE, "data", "full_graph.dot")
with open(dot_out, "w", encoding="utf-8") as f:
    f.write("\n".join(dot_lines))

print(f"\nGraph: {len(nodes)} nodes, {len(edges)} edges -> full_graph.dot")
print("Done!")
