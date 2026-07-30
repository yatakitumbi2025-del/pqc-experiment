#!/usr/bin/env python3
"""
rechunk.py — rebuild vectors.json from knowledge/*.md.

The gap this fills: build_vectors.py re-embeds the chunks ALREADY in
vectors.json. It never reads knowledge/*.md. So editing a knowledge file and
running build_vectors.py changes nothing — the markdown and the vectors drift
apart silently, and the pack keeps answering from the old chunks.

This re-splits every knowledge file into chunks (one per '## ' section, the
same rule make_pqc_repos.py used), writes them into vectors.json, then embeds
them. Run it INSTEAD of build_vectors.py whenever knowledge changes.

Preserves nothing from the old chunks except what the markdown still says —
that is the point. The markdown becomes the source of truth.

Usage, from any pack repo:
  cd ~/pqc-experiment
  python rechunk.py
  git add . && git commit -m "Update knowledge" && git push
"""

import glob
import json
import os
import sys

CORE_DIR = os.path.expanduser("~/modular-ai-core")
sys.path.insert(0, CORE_DIR)

try:
    import embed
except ImportError:
    print("Could not import embed.py from " + CORE_DIR)
    sys.exit(1)


def chunk_markdown(text, source_name):
    """One chunk per '## ' section. Same rule the pack generator used."""
    chunks = []
    title, lines = None, []

    def flush():
        if title and lines:
            body = "\n".join(lines).strip()
            if body:
                chunks.append({"text": title + "\n\n" + body,
                               "source": source_name})

    for line in text.splitlines():
        if line.startswith("## "):
            flush()
            title, lines = line[3:].strip(), []
        elif title is not None:
            lines.append(line)
    flush()
    return chunks


def rechunk_pack(pack_dir):
    pack_id = os.path.basename(pack_dir)
    knowledge = sorted(glob.glob(os.path.join(pack_dir, "knowledge", "*.md")))
    if not knowledge:
        print("  no knowledge/*.md — skipping")
        return 0

    chunks = []
    for path in knowledge:
        got = chunk_markdown(open(path).read(), os.path.basename(path))
        print("  " + os.path.basename(path).ljust(28) + str(len(got)) + " chunk(s)")
        chunks.extend(got)

    vpath = os.path.join(pack_dir, "vectors.json")
    old = 0
    if os.path.isfile(vpath):
        try:
            old = len(json.load(open(vpath)).get("chunks", []))
        except Exception:
            pass

    print("  embedding " + str(len(chunks)) + " chunk(s) via " + embed.MODEL + " ...")
    vectors = embed.embed([c["text"] for c in chunks])

    data = {
        "pack": pack_id,
        "embedding_model": embed.MODEL,
        "dimension": embed.DIM,
        "chunks": [
            {"id": pack_id + "-" + str(i), "text": c["text"],
             "source": c["source"], "vector": v}
            for i, (c, v) in enumerate(zip(chunks, vectors))
        ],
    }
    with open(vpath, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print("  vectors.json: " + str(old) + " -> " + str(len(chunks)) + " chunk(s)")
    return len(chunks)


def main():
    packs = sorted(glob.glob(os.path.join("packs", "*")))
    packs = [p for p in packs if os.path.isdir(p)]
    if not packs:
        print("No packs/ here. Run from inside a pack repo.")
        sys.exit(1)

    total = 0
    for pack_dir in packs:
        print(os.path.basename(pack_dir))
        total += rechunk_pack(pack_dir)
        print()

    print("Done. " + str(total) + " chunk(s) across "
          + str(len(packs)) + " pack(s).")
    print()
    print("Next:")
    print("  git add . && git commit -m 'Rechunk knowledge' && git push")
    print("  cd ~/pqc-assistant && rm -f routing_cache.json && rm -rf pack_cache")
    print()
    print("Note: retrieval pulls only the top 2 chunks per pack, so more")
    print("chunks means more competition. Adding knowledge is not free.")


if __name__ == "__main__":
    main()
