#!/usr/bin/env python3
"""
build_vectors.py — regenerate REAL embeddings for every domain pack.

Run this from the packs repo (~/modular-ai-packs). It borrows embed.py from
your core folder so the vectors it writes use the exact same model/dimension
as everything else. For each pack it re-embeds the knowledge chunks and
rewrites that pack's vectors.json, replacing the placeholder numbers.

Usage:
  cd ~/modular-ai-packs
  python build_vectors.py
  git add . && git commit -m "Real embeddings" && git push
"""

import os
import sys
import json
import glob

# Make embed.py (which lives in the core folder) importable from here.
CORE_DIR = os.path.expanduser("~/modular-ai-core")
sys.path.insert(0, CORE_DIR)

try:
    import embed
except ImportError:
    print(f"Could not import embed.py from {CORE_DIR}")
    print("Make sure embed.py is in your ~/modular-ai-core folder.")
    sys.exit(1)


def build_pack(vectors_path):
    data = json.loads(open(vectors_path).read())
    chunks = data.get("chunks", [])
    if not chunks:
        print("  (no chunks — skipping)")
        return 0

    texts = [c["text"] for c in chunks]
    print(f"  embedding {len(texts)} chunk(s) via Jina ...")
    vectors = embed.embed(texts)          # one API call for the whole pack

    for chunk, vec in zip(chunks, vectors):
        chunk["vector"] = vec

    # Update the header to reflect the real model, and drop the placeholder note.
    data["embedding_model"] = embed.MODEL
    data["dimension"] = embed.DIM
    data.pop("_note", None)

    with open(vectors_path, "w") as f:
        json.dump(data, f, indent=2)
    return len(chunks)


def main():
    paths = sorted(glob.glob("packs/*/vectors.json"))
    if not paths:
        print("No packs/*/vectors.json found.")
        print("Run this from inside ~/modular-ai-packs.")
        sys.exit(1)

    total = 0
    for path in paths:
        pack_id = path.split(os.sep)[1]
        print(f"pack: {pack_id}")
        total += build_pack(path)

    print(f"\nDone. Embedded {total} chunk(s) across {len(paths)} pack(s).")
    print("Vectors now use:", embed.MODEL, f"({embed.DIM} dims)")
    print("\nNext: git add . && git commit -m 'Real embeddings' && git push")


if __name__ == "__main__":
    main()
