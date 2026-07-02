# Accessibility sheet — incident-retro "The Debrief"

Target WCAG 2.2 AA. Implemented in `docs/index.html`.

## Measured contrast (WCAG 2.x)

### Clay (light)
| Pair | Ratio | Verdict |
|---|---|---|
| ink #2E1B1D / clay #F5E9E1 | 13.7:1 | AAA |
| soft #63494E / card #FDF6F1 | 7.57:1 | AAA |
| oxblood #8E2F3C / clay | 6.72:1 | AA+ |
| on-accent #FBF3F0 / oxblood | 7.32:1 | AAA |
| P3 green #356B4C / clay | 5.25:1 | AA |
| P2 amber #8A5A12 / clay | 4.96:1 | AA |
| P1 red #A02A2A / clay | 6.16:1 | AA+ |
| major blue #2F5878 / clay | 6.32:1 | AA+ |

### Late-hour (dark)
| Pair | Ratio | Verdict |
|---|---|---|
| ink #F2E6E4 / plum #201317 | 14.8:1 | AAA |
| soft #C4AEB2 / card #2B1B20 | 7.85:1 | AAA |
| dusk rose #E8909C / plum | 7.63:1 | AAA |
| on-accent #37131A / rose | 7.01:1 | AAA |
| low / med / high / major on plum | 9.64 / 9.38 / 7.39 / 9.64:1 | AAA |

Tinted pill backgrounds are ≤11% alpha; their text uses the solid colors above.

## Structure & ARIA (engine contracts preserved)
- Nav `.active` + view swap contract untouched; theme toggle adds
  `aria-pressed` + dynamic label. Hamburger retired visually (3 links fit;
  element remains hidden for the engine's binding).
- All form fields keep explicit `<label for>` pairs; editable doc fields
  (whys, factors, remediation actions, exec summary) have placeholders *plus*
  visible mono section labels.
- Severity/priority triple-encoded: pill color + text label + position.
- Breach/margin tiles pair color with explicit wording ("min over SLA (30)").
- Timeline gaps are worded chips ("23 minute gap with no recorded action").
- Reasoning receipt names model, task, timestamp; AI-fallback note is plain text.
- Print contract unchanged (chrome hidden, document flows on white).

## Keyboard
Topbar (nav pills → theme) → form fields in order → Build / Draft / Example →
document fields top-to-bottom → doc actions. All interactive elements have
two-layer oxblood `:focus-visible` rings; buttons ≥ 44px.

## Motion
One 420ms rise per view render; priority chips update with no animation
(state text change); hovers −1/−2px springs; no loops at all (the calm room
has nothing spinning). Full reduced-motion collapse.
