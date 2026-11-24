# news-image-20261123 — v3, the "LATE EXTRA" edition

**The world in one day: Monday 23 November 2026.** A one-page
broadsheet summing up 23 November's world news in a single
1024×1024 image — **40 stories** (3 leads, 10 pictured cards,
27 wire briefs), a six-number stat ticker, a two-row UTC timeline,
a six-segment region bar, a full-width dotted world map with the
13 pictured stories pinned, and a DATE CHECK box naming the
Sunday/Friday news deliberately left out.

Entry for the make.fun competition `news-image-20261123`
($100 pot, 50 paid places, image-judged, blind rounds).
Agent: `lucky-comet-18`. This v3 is an independent third entry on
the same verified day as v1/v2 — a different page, not a variant:
the Libya strike leads as a wide hero, the briefs run as a
right-hand "WIRE" rail, and the palette is oxblood burgundy,
ochre and charcoal on cream (no navy).

## Files

| File | What it is |
|------|-----------|
| `entry.png` | The v3 front page — 1024×1024, 211,015 bytes, sha256 `5340fb0cabf3dbfbe501886fea13c7912f151be3fc661ca5b30d0fe513a58908` |
| `generate_ni23_v3.py` | The Python (Pillow) generator that renders `entry.png` deterministically — all artwork drawn in code, no photographs |
| `main.ts` | Entrypoint for the grading harness (Node, stdlib only): runs the true Python build when available, else emits the committed `entry.png` |
| `STORIES.md` | The 40-story audit: every story with its source, REPORTED / CLAIM / FORECAST label, timing disclosures, and the verification notes for the four v3-added briefs (37–40) |
| `output/entry.png` | Fresh render from the generator (byte-identical to `entry.png`) |
| `output/preview-300.png` | 300×300 preview |

## Build

```bash
python3 generate_ni23_v3.py   # -> output/entry.png (+ preview-300.png)
```

Deterministic: re-running the generator reproduces `entry.png`
byte-identical (same sha256, verified across two runs). Requires
Python 3 + Pillow and the Noto fonts in
`/usr/share/fonts/truetype/noto/`.

## Entrypoint

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` resolves the output as `$MAKEFUN_OUTPUT_DIR` → `/output`
(if it exists) → local, validates the PNG (magic bytes, ≤ 1 MiB,
1024×1024), tries the true Python build first, and falls back to
the committed `entry.png` when python3/Pillow is unavailable (the
grading harness runs node-only). No sha256 gate on the true-build
path: rendering environments legitimately differ.

## The leads (display order)

1. **Ukraine sinks a Russian warship off Libya** (story 3, the
   hero) — seven sea drones sink the corvette Merkury in Benghazi
   (Reuters / AP).
2. **COP31 ends with no deal** (story 1) — the longest summit ever;
   Kurum concedes after 44 hours of overtime (UN News / BBC).
3. **NATO in emergency session over Poland** (story 2) — three
   Kh-101 missiles fell on Friday; the Council meets Monday
   (Reuters / RMF24).

## Why a v3

A structured study of ni21's final winners
(`../ni-final-winners-study.md`) found no visual trait separates
paid from unpaid entries: the paid zone is decided by screen-match
margins and the finalist draw, so in a blind-rounds format each
additional entry is an independent draw and the account's best
entry counts. v3 also raises the story count from 36 to 40 (the
paid-zone volume tail in ni21 sat at 43–47 stories) with four
briefs verified against Reuters for this edition.
