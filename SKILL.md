# Skill: incident-retro

## Name and Purpose

**incident-retro** generates a blameless post-incident review (RCA) document from
structured incident data. It computes all numerical facts deterministically in
Python and uses a DeepSeek language model only to draft prose (5-Whys chain,
contributing factors, executive summary, remediation actions). The model is
never trusted for numbers.

---

## When to Use

Use this skill after any production incident is resolved and you need to
produce a blameless RCA document for stakeholders. It is appropriate for
P1, P2, and P3 severity incidents where you have:

- A title and severity label
- An approximate user count and downtime duration
- An SLA target for the affected service
- A free-text description that may include timestamped timeline entries

---

## Inputs

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | Short incident title |
| `severity` | string | yes | One of P1, P2, P3 |
| `users_affected` | integer | yes | Number of users directly impacted |
| `downtime_min` | integer | yes | Total downtime in minutes |
| `sla_target_min` | integer | yes | SLA commitment in minutes |
| `description` | string | yes | Free text; lines beginning with HH:MM or H:MM are parsed as timeline events |

---

## Deterministic Logic

All calculations below are performed in Python. The AI model is never asked
to compute these values.

### 1. Timeline Parsing

Scan each line of `description` for the pattern `^\s*(\d{1,2})[:h](\d{2})\b`.
For each match, convert to minutes-of-day: `minutes = int(hour) * 60 + int(minute)`.
Sort matched events by minutes-of-day ascending.

For each pair of consecutive events, compute the gap:
```
gap = next_minutes - current_minutes
```
If `gap >= 15`, insert a synthetic entry:
```
"<gap> minute gap with no recorded action"
```
between the two events in the rendered timeline.

### 2. Blast Radius

```
user_minutes = users_affected * downtime_min
```

SLA status:

```
if downtime_min > sla_target_min:
    sla_status = f"BREACHED by {downtime_min - sla_target_min} min"
else:
    sla_status = f"MET with {sla_target_min - downtime_min} min margin"
```

### 3. Remediation Priority

Each remediation item carries `effort` in {S, M, L} and `impact` in
{Low, Medium, High}. Assign a priority label using this exact table:

| impact | effort | label |
|---|---|---|
| High | S | Quick win |
| High | M | Quick win |
| High | L | Major project |
| Medium | S | Planned |
| Medium | M | Planned |
| Medium | L | Planned |
| Low | S | Fill-in |
| Low | M | Reconsider |
| Low | L | Reconsider |

Sort the list so that higher-impact items appear first. Within the same
impact level, sort by lower effort first (S before M before L). Use the
ordering: High > Medium > Low for impact, and S < M < L for effort.

---

## The AI Prompt

The harness sends a single chat-completion request. Use the system prompt
below verbatim, substituting `{computed_facts}` and `{description}` at
runtime.

**System prompt (send as the "system" role message):**

```
You are a blameless post-incident analyst. You receive a computed facts
block and an incident description. Your job is to draft the prose sections
of a Root Cause Analysis document.

Rules:
- Return ONLY a single JSON object with no markdown fences, no commentary.
- Never invent, repeat, or rephrase any number. All figures are already in
  the facts block and will be inserted by the harness.
- Write in a blameless tone: describe systems, processes, and environmental
  conditions. Never name or blame any individual person.
- Do not use em dashes anywhere in your output. Use commas, colons, or
  parentheses instead.
- The JSON must have exactly these keys:
    "whys": array of 3 to 5 strings, each answering "why did the previous
            thing happen?", forming a causal chain.
    "factors": object with four array keys: "technical", "process",
               "human", "external". Each array holds short phrase strings.
               Arrays may be empty.
    "exec_summary": a string of 3 to 4 plain sentences suitable for a
                    non-technical reader. Reference the given numbers by
                    repeating the text from the facts block exactly; do not
                    invent new figures.
    "remediations": array of objects, each with keys:
                    "action" (string describing what to do),
                    "effort" (one of S, M, L),
                    "impact" (one of Low, Medium, High).
```

**User message:**

```
COMPUTED FACTS:
{computed_facts}

INCIDENT DESCRIPTION:
{description}

Return JSON only.
```

**API details:**

- Endpoint: `https://integrate.api.nvidia.com/v1/chat/completions`
- Header: `Authorization: Bearer ${NVIDIA_API_KEY}`
- Default model: `deepseek-ai/deepseek-v4-flash`
- Best model for 5-Whys reasoning: `deepseek-ai/deepseek-v4-pro`
- Alternative model: `minimaxai/minimax-m3`

---

## Truth Guard Rules

1. The harness computes every number (user_minutes, SLA breach/margin,
   timeline gaps) before calling the model.
2. The model response is parsed for prose fields only: `whys`, `factors`,
   `exec_summary`, and the non-numeric parts of `remediations`.
3. `effort` and `impact` values from `remediations` are accepted only if
   they are exactly one of the allowed symbols (S, M, L) or words
   (Low, Medium, High). They carry no numbers.
4. If the model emits a digit in `exec_summary` or `whys`, that sentence
   is flagged with "(model-supplied number, verify)" but the harness's own
   computed numbers in the blast-radius and SLA sections are never replaced.
5. If the model response cannot be parsed as valid JSON, the prose sections
   are left as "(fill in)" and the document is still assembled from computed
   facts.

---

## Output Layout

The assembled RCA is printed as Markdown with the following sections in
order:

```
# RCA: {title}

**Severity:** {severity}
**Date:** {date}

## Blast Radius

- Users affected: {users_affected}
- Downtime: {downtime_min} min
- User-minutes lost: {user_minutes}
- SLA target: {sla_target_min} min -- {sla_status}

## Timeline

| Time | Event |
|------|-------|
| HH:MM | event text |
| (gap) | N minute gap with no recorded action |
...

## 5-Whys Root Cause Chain

1. {why_1}
2. {why_2}
...

## Contributing Factors

**Technical:** ...
**Process:** ...
**Human:** ...
**External:** ...

## Remediations

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| Quick win | ... | S | High |
...

## Executive Summary

{exec_summary}
```

---

## Worked Example: Sandton POS Incident

**Inputs:**

```python
title          = "Sandton POS payment gateway timeout"
severity       = "P2"
users_affected = 6
downtime_min   = 48
sla_target_min = 30
description    = """
09:15 Alerts fired for payment gateway timeouts across Sandton stores.
09:22 On-call engineer paged and acknowledged.
09:55 Root cause identified as expired TLS certificate on gateway proxy.
10:03 Certificate renewed and service restored.
"""
```

**Deterministic results:**

Timeline events extracted:
- 09:15 (555 min), 09:22 (562 min), 09:55 (595 min), 10:03 (603 min)

Gaps:
- 09:22 to 09:55 = 33 minutes (>= 15, flagged)

Blast radius:
- user_minutes = 6 * 48 = 288
- SLA: 48 > 30, so BREACHED by 18 min

Remediation example (if model returns these):

| action | effort | impact |
|---|---|---|
| Automate TLS certificate renewal | S | High |
| Add certificate expiry monitoring | S | High |
| Improve on-call runbook for gateway issues | M | Medium |

After priority sort:

| Priority | Action | Effort | Impact |
|---|---|---|---|
| Quick win | Automate TLS certificate renewal | S | High |
| Quick win | Add certificate expiry monitoring | S | High |
| Planned | Improve on-call runbook for gateway issues | M | Medium |

**Expected RCA header (computed section):**

```
# RCA: Sandton POS payment gateway timeout

**Severity:** P2

## Blast Radius

- Users affected: 6
- Downtime: 48 min
- User-minutes lost: 288
- SLA target: 30 min -- BREACHED by 18 min

## Timeline

| Time | Event |
|------|-------|
| 09:15 | Alerts fired for payment gateway timeouts across Sandton stores. |
| 09:22 | On-call engineer paged and acknowledged. |
| (gap) | 33 minute gap with no recorded action |
| 09:55 | Root cause identified as expired TLS certificate on gateway proxy. |
| 10:03 | Certificate renewed and service restored. |
```
