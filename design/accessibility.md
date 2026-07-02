# Accessibility sheet — incident-retro v3 "The Learning Board"

Target WCAG 2.2 AA. Implemented in `docs/index.html`.

## Measured contrast (WCAG 2.x)

### Board (graphite, default)
| Pair | Ratio | Verdict |
|---|---|---|
| bone #F2F1EC / graphite #161614 | 16.0:1 | AAA |
| soft #B9B7AC / surface #21201C | 8.1:1 | AAA |
| mute #8F8D82 / graphite | 5.44:1 | AA |
| lime #C8F135 / graphite | 13.9:1 | AAA |
| on-lime ink #1A2400 / lime | 12.4:1 | AAA |
| lime-text #D6EE63 / surface | 12.6:1 | AAA |
| P1 #FF8577 · P2 #F0C24B · P3 #6FD08F / graphite | 7.7 / 10.8 / 9.6:1 | AAA |
| major #8FB8FF / graphite | 9.0:1 | AAA |

### Daylight (paper)
| Pair | Ratio | Verdict |
|---|---|---|
| ink #1D1C18 / paper #F4F4EF | 15.5:1 | AAA |
| soft #565550 / card | 7.5:1 | AAA |
| lime-deep text #4E6B00 / paper | 5.55:1 | AA |
| on-lime #1A2400 / lime plate #B7E62B | 11.1:1 | AAA |
| P1 / P2 / P3 / major on paper | 6.7 / 6.0 / 5.5 / 6.8:1 | AA+ |

## Structure, ARIA, keyboard — engine contracts preserved
Nav `.active` (lime-filled) + `aria-pressed` theme toggle · labelled fields ·
severity/priority triple-encoded (chip color + text + inset ring) · breach
and margin tiles carry explicit wording · gap chips are worded · receipts
plain-text · print contract unchanged · two-layer lime focus rings ≥ all
interactive elements · buttons ≥ 44px.

## Mobile a11y
Form fonts 16px ≤560px (prevents iOS auto-zoom on focus) · targets keep 44px
· dock nav horizontally scrollable (no wrap, no overlap) · priority chips
become full-width rows ≤480px so selects never collide · long titles/receipts
wrap with `overflow-wrap:anywhere` — nothing overflows at 360px.

## Motion
One 400ms rise per view; spring hovers; zero loops. Full reduced-motion
collapse.
