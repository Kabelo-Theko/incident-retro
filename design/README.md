# incident-retro — "The Debrief" design system

**Project:** [incident-retro](https://github.com/Kabelo-Theko/incident-retro) · **Complete UI/UX overhaul, July 2026** (built at the recalibrated 2026 bar)

## The concept

A blameless review happens in **the calm hour after the fire** — and the design
is that hour: blush-clay warmth, oxblood ink, an elegant Instrument Serif that
gives the document the gravity of something worth keeping. Numbers stay
sacred: the blast radius is *computed*, marked with its own italic truth line,
and the AI (when invited) only drafts wording that a person reviews.

### Design DNA

| | |
|---|---|
| **Essence** | A debrief room, not an alarm room. Reflection with rigour. |
| **One-liner** | "A mediation-trained senior engineer hired to run the post-mortem." |
| **Canvas** | Blush clay `#F5E9E1` (default) · late-hour plum `#201317` |
| **Accent** | Oxblood `#8E2F3C` / dusk rose `#E8909C` by night — eyebrow, times, primary actions. Severity and priority are 10%-alpha tinted pills (P1 red / P2 amber / P3 green; Quick win green / Major blue / Planned amber / Reconsider red). |
| **Type cast** | Instrument Serif 400 + italic (display, doc titles, the big blast numerals) · Switzer (text, Fontshare) · Space Mono (timestamps, receipts, section labels, chips) |
| **Shape** | 12–22px radii, pill chips and segmented nav — soft, deliberate |
| **Signature** | The segmented-track nav with a floating active pill; serif blast-radius numerals at 2rem on clay tiles; mono timeline times in oxblood; the italic "computed, not generated" truth line |
| **Rejection list** | No alarm styling (this is *after* the incident), no cold blue-gray (v1 retired), no Inter/Archivo, no hard corners, no left-border cards |

## Functional parity (zero loss — engine untouched)

The engine ships byte-identical: timeline parser with gap detection, computed
blast radius + SLA breach/margin, 5-Whys editable chain, factor buckets,
effort×impact priority chips (live re-ranked), executive summary
(template or AI draft with reasoning receipt + no-key fallback), Markdown
copy/download ordered quick-wins-first, print contract, localStorage library
(open/copy/delete), URL-param prefill, the worked Sandton example.

New: clay/late-hour themes (persisted), segmented pill nav + theme toggle,
Instrument Serif document voice, spring hovers, 90% 4px grid, audit
0 fails / 0 warnings.

## Files
`tokens.css` · `tailwind.config.js` · `components.md` · `accessibility.md` ·
`motion.md` · `grid.md` (icon-light by design: moon/sun toggle only; mono
labels carry the wayfinding).

## Reaching every state
| State | How |
|---|---|
| Empty debrief | Load the app |
| Worked example | "See an example" — Sandton POS P1 with breach tile |
| Deterministic skeleton | Fill the form → Build RCA |
| AI draft + receipt / fallback | Draft with AI (offline shows the no-key note under the doc) |
| Breach vs margin tiles | Set downtime above/below the SLA target |
| Timeline gaps | Leave ≥15 min between timestamped lines |
| Priority chips live | Change effort/impact selects — chips re-label instantly |
| Library / empty | Save to library → Library tab; delete all for empty state |
| Late-hour theme | Moon toggle; persists |
