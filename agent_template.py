"""
agent_template.py
-----------------
Runnable Python 3 agent harness for the incident-retro skill.

Truth Guard: all numbers are computed here in Python. The DeepSeek model
receives only the description and the pre-computed fact string. It is
asked to return prose only. Any digit found in the model's exec_summary
or whys fields is flagged but the harness's own computed numbers are
never replaced.

Dependencies: Python 3 standard library only (urllib.request, json, os,
re, datetime).

Usage:
    python3 agent_template.py
    NVIDIA_API_KEY=sk-... python3 agent_template.py
"""

import json
import os
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
# Override via MODEL env var, e.g. MODEL=deepseek-ai/deepseek-v4-pro
MODEL = os.environ.get("MODEL", "deepseek-ai/deepseek-v4-flash")
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# ---------------------------------------------------------------------------
# Deterministic core functions (Truth Guard: numbers live here, not in AI)
# ---------------------------------------------------------------------------

def parse_timeline(description: str) -> list:
    """
    Parse lines matching HH:MM or H:MM (or H:MM or HH[h]MM) from description.
    Returns a list of dicts: {"minutes": int, "time_str": str, "text": str}
    sorted ascending by minutes-of-day.

    Between consecutive events, if the gap is >= 15 minutes a synthetic gap
    entry is inserted: {"minutes": None, "time_str": "(gap)", "text": "N minute gap with no recorded action"}
    """
    pattern = re.compile(r'^\s*(\d{1,2})[:h](\d{2})\b(.*)', re.IGNORECASE)
    raw_events = []

    for line in description.splitlines():
        match = pattern.match(line)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            text = match.group(3).strip()
            # Reconstruct a clean time string
            time_str = f"{hour:02d}:{minute:02d}"
            minutes_of_day = hour * 60 + minute
            raw_events.append({
                "minutes": minutes_of_day,
                "time_str": time_str,
                "text": text if text else line.strip(),
            })

    # Sort by time ascending
    raw_events.sort(key=lambda e: e["minutes"])

    # Insert gap markers between consecutive events where gap >= 15 min
    result = []
    for i, event in enumerate(raw_events):
        result.append(event)
        if i < len(raw_events) - 1:
            next_event = raw_events[i + 1]
            gap = next_event["minutes"] - event["minutes"]
            if gap >= 15:
                result.append({
                    "minutes": None,
                    "time_str": "(gap)",
                    "text": f"{gap} minute gap with no recorded action",
                })

    return result


def blast_radius(users_affected: int, downtime_min: int, sla_target_min: int) -> dict:
    """
    Compute blast radius metrics deterministically.
    Returns a dict with user_minutes and sla_status string.
    """
    user_minutes = users_affected * downtime_min

    if downtime_min > sla_target_min:
        sla_status = f"BREACHED by {downtime_min - sla_target_min} min"
    else:
        sla_status = f"MET with {sla_target_min - downtime_min} min margin"

    return {
        "user_minutes": user_minutes,
        "sla_status": sla_status,
    }


def priority(effort: str, impact: str) -> str:
    """
    Assign a remediation priority label from effort (S/M/L) and
    impact (Low/Medium/High).

    Mapping:
        High + S or M  -> "Quick win"
        High + L       -> "Major project"
        Medium + any   -> "Planned"
        Low + S        -> "Fill-in"
        otherwise      -> "Reconsider"
    """
    effort = effort.strip().upper()
    impact = impact.strip().capitalize()

    if impact == "High":
        if effort in ("S", "M"):
            return "Quick win"
        else:
            return "Major project"
    elif impact == "Medium":
        return "Planned"
    elif impact == "Low":
        if effort == "S":
            return "Fill-in"
        else:
            return "Reconsider"
    else:
        return "Reconsider"


def _impact_rank(impact: str) -> int:
    """Return a sort key so High sorts first (lower number = higher rank)."""
    return {"High": 0, "Medium": 1, "Low": 2}.get(impact.capitalize(), 3)


def _effort_rank(effort: str) -> int:
    """Return a sort key so S sorts first."""
    return {"S": 0, "M": 1, "L": 2}.get(effort.upper(), 3)


def sort_remediations(remediations: list) -> list:
    """
    Sort remediation items: higher impact first, then lower effort first.
    Each item must have "effort" and "impact" keys.
    """
    return sorted(
        remediations,
        key=lambda r: (_impact_rank(r.get("impact", "")), _effort_rank(r.get("effort", ""))),
    )


def facts_string(
    title: str,
    severity: str,
    users_affected: int,
    downtime_min: int,
    sla_target_min: int,
    blast: dict,
) -> str:
    """
    Build the computed-facts block that is passed to the AI model.
    This contains all numbers so the model can reference them in prose
    without inventing new figures.
    """
    lines = [
        f"Incident title: {title}",
        f"Severity: {severity}",
        f"Users affected: {users_affected}",
        f"Downtime: {downtime_min} min",
        f"SLA target: {sla_target_min} min",
        f"User-minutes lost: {blast['user_minutes']}",
        f"SLA status: {blast['sla_status']}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# AI layer (optional, controlled by NVIDIA_API_KEY)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a blameless post-incident analyst. You receive a computed facts "
    "block and an incident description. Your job is to draft the prose sections "
    "of a Root Cause Analysis document.\n\n"
    "Rules:\n"
    "- Return ONLY a single JSON object with no markdown fences, no commentary.\n"
    "- Never invent, repeat, or rephrase any number. All figures are already in "
    "the facts block and will be inserted by the harness.\n"
    "- Write in a blameless tone: describe systems, processes, and environmental "
    "conditions. Never name or blame any individual person.\n"
    "- Do not use em dashes anywhere in your output. Use commas, colons, or "
    "parentheses instead.\n"
    "- The JSON must have exactly these keys:\n"
    '    "whys": array of 3 to 5 strings, each answering "why did the previous '
    'thing happen?", forming a causal chain.\n'
    '    "factors": object with four array keys: "technical", "process", '
    '"human", "external". Each array holds short phrase strings. Arrays may be empty.\n'
    '    "exec_summary": a string of 3 to 4 plain sentences suitable for a '
    "non-technical reader. Reference the given numbers by repeating the text "
    "from the facts block exactly; do not invent new figures.\n"
    '    "remediations": array of objects, each with keys:\n'
    '                    "action" (string describing what to do),\n'
    '                    "effort" (one of S, M, L),\n'
    '                    "impact" (one of Low, Medium, High).\n'
)


def call_deepseek(facts: str, description: str, api_key: str) -> dict:
    """
    Call the DeepSeek model via NVIDIA's endpoint.
    Returns parsed JSON dict on success, or an empty dict on failure.
    """
    user_message = (
        "COMPUTED FACTS:\n"
        f"{facts}\n\n"
        "INCIDENT DESCRIPTION:\n"
        f"{description}\n\n"
        "Return JSON only."
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        NVIDIA_API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        print(f"[WARNING] DeepSeek API error {exc.code}: {exc.read().decode('utf-8', errors='replace')}")
        return {}
    except Exception as exc:
        print(f"[WARNING] DeepSeek call failed: {exc}")
        return {}

    try:
        outer = json.loads(raw)
        content = outer["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        print(f"[WARNING] Unexpected API response shape: {exc}")
        return {}

    # Strip accidental markdown fences if the model adds them despite instructions
    content = re.sub(r"^```[a-z]*\n?", "", content.strip())
    content = re.sub(r"\n?```$", "", content.strip())

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        print(f"[WARNING] Model response is not valid JSON: {exc}")
        print(f"[DEBUG] Raw content: {content[:500]}")
        return {}

    return parsed


# ---------------------------------------------------------------------------
# Truth Guard: validate and sanitise model output
# ---------------------------------------------------------------------------

def _contains_digit(text: str) -> bool:
    """Return True if the string contains any decimal digit."""
    return bool(re.search(r'\d', text))


def apply_truth_guard(prose: dict) -> dict:
    """
    Accept only prose from the model. Flag any string that contains a digit.
    Never overwrite computed numbers.
    """
    guarded = {}

    # whys: flag individual items that contain digits
    whys_raw = prose.get("whys", [])
    if isinstance(whys_raw, list):
        guarded["whys"] = [
            (w + "  (model-supplied number, verify)" if _contains_digit(str(w)) else str(w))
            for w in whys_raw
        ]
    else:
        guarded["whys"] = []

    # factors: accept as-is (they are short phrases, unlikely to carry numbers)
    factors_raw = prose.get("factors", {})
    if isinstance(factors_raw, dict):
        guarded["factors"] = {
            k: [str(v) for v in vals] if isinstance(vals, list) else []
            for k, vals in factors_raw.items()
        }
    else:
        guarded["factors"] = {"technical": [], "process": [], "human": [], "external": []}

    # exec_summary: flag if it contains digits
    summary_raw = prose.get("exec_summary", "")
    if isinstance(summary_raw, str):
        if _contains_digit(summary_raw):
            guarded["exec_summary"] = summary_raw + "  (model-supplied number, verify)"
        else:
            guarded["exec_summary"] = summary_raw
    else:
        guarded["exec_summary"] = "(fill in)"

    # remediations: accept action (prose), effort, impact only
    rems_raw = prose.get("remediations", [])
    valid_efforts = {"S", "M", "L"}
    valid_impacts = {"Low", "Medium", "High"}
    guarded_rems = []
    if isinstance(rems_raw, list):
        for item in rems_raw:
            if not isinstance(item, dict):
                continue
            action = str(item.get("action", "")).strip()
            effort = str(item.get("effort", "")).strip().upper()
            impact = str(item.get("impact", "")).strip().capitalize()
            if effort not in valid_efforts:
                effort = "M"  # safe default
            if impact not in valid_impacts:
                impact = "Low"  # safe default
            guarded_rems.append({"action": action, "effort": effort, "impact": impact})
    guarded["remediations"] = guarded_rems

    return guarded


# ---------------------------------------------------------------------------
# Markdown assembly
# ---------------------------------------------------------------------------

def build_markdown(
    title: str,
    severity: str,
    users_affected: int,
    downtime_min: int,
    sla_target_min: int,
    blast: dict,
    timeline: list,
    prose: dict,
    date_str: str,
) -> str:
    """
    Assemble the final RCA Markdown document.
    All numbers come from the Python-computed arguments, never from prose.
    """
    lines = []

    # Header
    lines.append(f"# RCA: {title}")
    lines.append("")
    lines.append(f"**Severity:** {severity}")
    lines.append(f"**Date:** {date_str}")
    lines.append("")

    # Blast radius (all computed)
    lines.append("## Blast Radius")
    lines.append("")
    lines.append(f"- Users affected: {users_affected}")
    lines.append(f"- Downtime: {downtime_min} min")
    lines.append(f"- User-minutes lost: {blast['user_minutes']}")
    lines.append(f"- SLA target: {sla_target_min} min, {blast['sla_status']}")
    lines.append("")

    # Timeline
    lines.append("## Timeline")
    lines.append("")
    if timeline:
        lines.append("| Time | Event |")
        lines.append("|------|-------|")
        for entry in timeline:
            time_str = entry["time_str"]
            text = entry["text"].replace("|", "/")
            lines.append(f"| {time_str} | {text} |")
    else:
        lines.append("No timestamped events found in description.")
    lines.append("")

    # 5-Whys
    lines.append("## 5-Whys Root Cause Chain")
    lines.append("")
    whys = prose.get("whys", [])
    if whys:
        for i, why in enumerate(whys, start=1):
            lines.append(f"{i}. {why}")
    else:
        lines.append("(fill in)")
    lines.append("")

    # Contributing factors
    lines.append("## Contributing Factors")
    lines.append("")
    factors = prose.get("factors", {})
    for category in ("technical", "process", "human", "external"):
        items = factors.get(category, [])
        label = category.capitalize()
        if items:
            lines.append(f"**{label}:** {', '.join(items)}")
        else:
            lines.append(f"**{label}:** (none identified)")
    lines.append("")

    # Remediations
    lines.append("## Remediations")
    lines.append("")
    rems = prose.get("remediations", [])
    if rems:
        sorted_rems = sort_remediations(rems)
        lines.append("| Priority | Action | Effort | Impact |")
        lines.append("|----------|--------|--------|--------|")
        for item in sorted_rems:
            action = item.get("action", "")
            effort = item.get("effort", "")
            impact = item.get("impact", "")
            prio = priority(effort, impact)
            lines.append(f"| {prio} | {action} | {effort} | {impact} |")
    else:
        lines.append("(fill in)")
    lines.append("")

    # Executive summary
    lines.append("## Executive Summary")
    lines.append("")
    summary = prose.get("exec_summary", "(fill in)")
    lines.append(summary)
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main: Sandton POS demo (runs with no arguments)
# ---------------------------------------------------------------------------

def main():
    # Sandton POS demo incident (hardcoded as required by the skill spec)
    title = "Sandton POS payment gateway timeout"
    severity = "P2"
    users_affected = 6
    downtime_min = 48
    sla_target_min = 30
    description = (
        "09:15 Alerts fired for payment gateway timeouts across Sandton stores.\n"
        "09:22 On-call engineer paged and acknowledged.\n"
        "09:55 Root cause identified as expired TLS certificate on gateway proxy.\n"
        "10:03 Certificate renewed and service restored.\n"
    )

    # Deterministic computations (Truth Guard: numbers live here)
    blast = blast_radius(users_affected, downtime_min, sla_target_min)
    timeline = parse_timeline(description)
    facts = facts_string(title, severity, users_affected, downtime_min, sla_target_min, blast)

    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    # AI layer (optional)
    api_key = os.environ.get("NVIDIA_API_KEY")
    prose = {}

    if api_key:
        print(f"[INFO] Calling DeepSeek model: {MODEL}")
        raw_prose = call_deepseek(facts, description, api_key)
        if raw_prose:
            prose = apply_truth_guard(raw_prose)
        else:
            print("[INFO] Model call returned no usable output; prose sections set to (fill in).")
    else:
        print("[INFO] NVIDIA_API_KEY not set; skipping AI layer. Prose sections will be (fill in).")

    # Fill defaults for prose sections if AI was skipped or failed
    prose.setdefault("whys", [])
    prose.setdefault("factors", {"technical": [], "process": [], "human": [], "external": []})
    prose.setdefault("exec_summary", "(fill in)")
    prose.setdefault("remediations", [])

    # Assemble and print the RCA
    rca = build_markdown(
        title=title,
        severity=severity,
        users_affected=users_affected,
        downtime_min=downtime_min,
        sla_target_min=sla_target_min,
        blast=blast,
        timeline=timeline,
        prose=prose,
        date_str=date_str,
    )

    print(rca)


if __name__ == "__main__":
    main()
