# Responsive grid & layout — incident-retro "The Learning Board"

## Breakpoints
| Width | Changes |
|---|---|
| ≤ 380px | grid2 field pairs stack |
| ≤ 480px | priority chips become full-width rows |
| ≤ 560px | form fonts go 16px (iOS zoom guard) |
| ≤ 600px | Blast metrics 4→2-up; factor buckets stack |
| ≤ 920px | Desk collapses; form panel un-sticks above the document |
| 1120px | `--page-max` |

Checked at 360 / 768 / 1280.

## Structure
```
topbar: ● incident-retro · [Build RCA | Library | Reference] · ◐
mast: lime-dash eyebrow → Cabinet 800 H1 (lime lesson) → lede
desk: [form panel 360px sticky | document 1fr]
  document: label → serif title → sev pill + stamp
    → blast tiles (4 → 2) + truth line
    → timeline → 5-Whys → factors (2×2 → 1)
    → remediations → exec summary → receipt → doc bar
library: card list · reference: serif prose
```

## Rhythm
4px grid (90% audited). Panel 24px interior; document 36px with mono section
rules every 32px; masthead 48px top. Radii: 12 (fields) / 14 (tiles) /
22 (cards, document) / pill (nav, chips, buttons).
