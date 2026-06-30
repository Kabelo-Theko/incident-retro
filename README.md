# incident-retro

**Built for:** IT Support · Junior Business Analyst · IT Manager

**Live demo:** _(create the repo, deploy on Vercel, add NVIDIA_API_KEY, then paste the URL here)_

**Outcome:** turns a resolved incident into a blameless post-incident review in about two minutes, the write-up a senior support engineer is expected to run and the same artefact a business analyst produces on an impact-analysis ticket. It replaces a blank page and an hour of formatting with a structured review whose every number can be defended.

It is the reflection step after a ticket is closed in [ticket-triage](https://github.com/Kabelo-Theko/ticket-triage) and written up in [resolve-notes](https://github.com/Kabelo-Theko/resolve-notes-): where resolve-notes captures the fix, incident-retro captures why it happened and what to change.

## What it produces

- A **timeline** rebuilt from your notes (any line that starts with a time), with gaps flagged.
- A **computed blast radius**: users affected, downtime, user-minutes lost, and SLA breach or margin.
- A **5-Whys** chain (a real chain, each why answering the one before).
- **Contributing factors** split into technical, process, human and external.
- Three **remediations** scored by effort against impact (Quick win, Major project, Planned, Fill-in, Reconsider), ordered so the quick wins sit at the top.
- A plain-English **executive summary** for a non-technical reader.

Export as Markdown, download, save to a local library, or print.

## The numbers are computed, not generated

Blast radius and SLA status come straight from the figures you enter. Users affected times downtime gives user-minutes lost; downtime against the SLA target gives the breach or the margin. The model never touches a number. That is the line that makes the output defensible: every figure traces back to an input.

## How the AI is used

Optional, and only at the edges. The model drafts wording (the 5-Whys, the factor lists, the executive summary) and is fed the incident text plus the already-computed facts so it cannot invent figures. Every draft carries a reasoning receipt and is yours to edit before it leaves the page. With no key set, **Build RCA** and the example both work.

The model is switchable: **DeepSeek v4 Flash** (fast, default), **DeepSeek v4 Pro** (best for the multi-step 5-Whys reasoning), or **MiniMax M3**.

## Run / deploy

A static front end in `docs/` plus one serverless function in `api/`.

- **Vercel:** import the repo, add `NVIDIA_API_KEY` in Settings, Environment Variables, deploy. `vercel.json` serves `docs/` and runs `api/ai.js` (up to 60s for the Pro reasoning chain).
- **Static only (no AI):** open `docs/index.html`; the deterministic skeleton and the example work without a backend.

## Where your data goes

The library is stored in your browser. The only thing that leaves is the incident text you submit for an AI draft, which goes to the model API. Nothing else.

## Licence

MIT.
