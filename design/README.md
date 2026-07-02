# incident-retro — "The Learning Board" design system (v3)

**Project:** [incident-retro](https://github.com/Kabelo-Theko/incident-retro) · **v3, July 2026**
*(v2's blush-clay/oxblood register was retired after review — it read muted
and washed. v3 goes the other way: high contrast, confident, modern.)*

## The concept

A good post-incident review ends on **the lesson** — so the design is a
learning board: graphite surface, bone ink, and one **signal-lime marker**
that highlights exactly what matters (the eyebrow dash, the lesson word in
the headline, timeline times, Quick-win actions, the primary button). The
blast radius reads as a **scoreboard** — big Cabinet Grotesk numerals on
inset tiles, the breach tile ringed red — with a lime-ruled
*computed-not-generated* line beneath. A clean **daylight** paper theme ships
for bright rooms.

### Design DNA

| | |
|---|---|
| **Essence** | The board where the team writes down the lesson. High contrast, zero blame. |
| **One-liner** | "A sports analyst's board hired for blameless engineering reviews." |
| **Canvas** | Graphite `#161614` (board, default) · paper `#F4F4EF` (daylight) |
| **Accent** | Signal lime `#C8F135` (13.9:1 on graphite; dark ink on lime 12.4:1) — the lesson marker. Quick-win priority chips go solid lime; P1/P2/P3 and Major/Planned/Reconsider stay tinted chips with inset rules. |
| **Type cast** | Cabinet Grotesk 700/800 (display + scoreboard numerals, Fontshare) · Supreme (text, Fontshare) · Space Mono (times, receipts) |
| **Shape** | 12–18px radii, pill dock nav (lime-filled active), squared metric tiles |
| **Signature** | The scoreboard blast tiles with ringed breach/margin; lime timeline times; the lime-ruled truth line; "What broke. Why. *What changes.*" |
| **Rejection list** | No muted/dusty palettes (v2's failure), no serif (this board is grotesk), no left-border cards, no loops |

## Functional parity (zero loss — engine untouched)
Timeline parser + gap chips, computed blast radius + SLA breach/margin,
editable 5-Whys/factors/remediations with live priority chips, exec summary
(template or AI draft + receipt + no-key fallback), Markdown export
(quick wins first), print contract, localStorage library, URL prefill, the
Sandton worked example.

## Mobile hardening (v3)
16px form fonts ≤560px (no iOS focus zoom) · `min-width:0` on all grid/flex
children · `overflow-x:clip` on body · `overflow-wrap:anywhere` on titles,
receipts, gap chips · metrics 4→2-up ≤600px · grid2 stacks ≤380px · priority
chips drop to full-width rows ≤480px · dock nav scrolls, never wraps over
content. Audit: **0 fails, 0 warnings, 94% 4px grid.**

## Reaching every state
| State | How |
|---|---|
| Empty board / worked example | Load → "See an example" (Sandton P1, breach tile ringed) |
| Deterministic skeleton / AI draft / fallback | Build RCA · Draft with AI (offline → note) |
| Breach vs margin tiles | Downtime above/below the SLA target |
| Gap chips · live priority chips · library | as v2 |
| Daylight theme | Sun/moon toggle; persists |
