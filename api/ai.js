// incident-retro: AI serverless harness (Vercel function).
// Task "rca" (default): from an incident description plus the app's computed facts,
//   draft the blameless reasoning: a 5-Whys chain, contributing factors split into
//   technical / process / human / external, three remediations with effort and impact,
//   and a plain-English executive summary. The app computes every NUMBER (blast radius,
//   SLA impact); the model only drafts prose, and a human reviews it.
// Model toggle: flash (default) / pro / minimax. One NVIDIA_API_KEY powers all.

const ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions";
const MODELS = {
  flash:   { id: "deepseek-ai/deepseek-v4-flash", keys: ["NVIDIA_API_KEY_FLASH", "NVIDIA_API_KEY"], extra: { chat_template_kwargs: { thinking: false } } },
  pro:     { id: "deepseek-ai/deepseek-v4-pro",   keys: ["NVIDIA_API_KEY_PRO", "NVIDIA_API_KEY"],   extra: { chat_template_kwargs: { thinking: false } } },
  minimax: { id: "minimaxai/minimax-m3",          keys: ["NVIDIA_API_KEY_MINIMAX", "NVIDIA_API_KEY"], extra: {} },
};
const cfgFor = (m) => MODELS[m] || MODELS.flash;
const keyFor = (c) => { for (const e of c.keys) { if (process.env[e]) return process.env[e]; } return null; };
async function readBody(req) {
  let b = req.body;
  if (typeof b === "string") { try { b = JSON.parse(b); } catch { b = {}; } }
  if (!b) { b = await new Promise((res) => { let raw = ""; req.on("data", c => raw += c); req.on("end", () => { try { res(JSON.parse(raw || "{}")); } catch { res({}); } }); }); }
  return b || {};
}
const jsonFrom = (t) => { const m = t.match(/\{[\s\S]*\}/); if (!m) return null; try { return JSON.parse(m[0]); } catch { return null; } };
async function callModel(cfg, key, messages, max_tokens, temperature) {
  const payload = { model: cfg.id, messages, max_tokens, temperature, top_p: 0.95, stream: false, ...cfg.extra };
  const ctrl = new AbortController(); const to = setTimeout(() => ctrl.abort(), 55000);
  try {
    const r = await fetch(ENDPOINT, { method: "POST", headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: ctrl.signal });
    clearTimeout(to);
    if (!r.ok) return { error: "upstream " + r.status };
    const d = await r.json();
    return { text: (d.choices?.[0]?.message?.content || "").trim() };
  } catch (e) { clearTimeout(to); return { error: "request failed" }; }
}

const SHAPE = `{"whys":["<why 1>","<why 2>","<why 3>"],"factors":{"technical":["<factor>"],"process":["<factor>"],"human":["<factor>"],"external":["<factor>"]},"exec_summary":"<3 to 4 plain sentences for a non-technical reader>","remediations":[{"action":"<action>","effort":"S","impact":"High"}]}`;
const SYS_RCA = `You are a senior incident manager writing a BLAMELESS post-incident review. Blameless means you describe systems, process and conditions, never blaming a named person. You are given an incident description and the facts the app has already computed (users affected, downtime, SLA target). Respond ONLY with compact JSON in this exact shape:
${SHAPE}
Rules: 3 to 5 "whys", each building on the one before (this is a 5-Whys chain, so each why answers the previous). 1 to 4 items per factor bucket; leave a bucket as an empty array if nothing applies. Exactly 3 remediations; effort is one of S, M, L; impact is one of Low, Medium, High. The exec_summary must use the computed numbers as given and must not invent any new numbers. Be factual and concise. No fluff, no marketing words, no em dashes.`;

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ error: "POST only" }); return; }
  const body = await readBody(req);
  const cfg = cfgFor(body.model);
  const key = keyFor(cfg);
  if (!key) { res.status(503).json({ error: "AI backend not configured" }); return; }

  const incident = (body.incident || "").toString().slice(0, 3500).trim();
  const facts = (body.facts || "").toString().slice(0, 600).trim();
  if (!incident) { res.status(400).json({ error: "no incident" }); return; }
  const user = `Incident description:\n${incident}\n\nComputed facts (use these numbers, do not change them):\n${facts}`;
  const out = await callModel(cfg, key, [{ role: "system", content: SYS_RCA }, { role: "user", content: user }], 900, 0.3);
  if (out.error) { res.status(502).json({ error: out.error }); return; }
  const j = jsonFrom(out.text); if (!j) { res.status(502).json({ error: "could not parse model output" }); return; }
  res.status(200).json({
    whys: Array.isArray(j.whys) ? j.whys.slice(0, 5) : [],
    factors: {
      technical: Array.isArray(j.factors?.technical) ? j.factors.technical : [],
      process: Array.isArray(j.factors?.process) ? j.factors.process : [],
      human: Array.isArray(j.factors?.human) ? j.factors.human : [],
      external: Array.isArray(j.factors?.external) ? j.factors.external : [],
    },
    exec_summary: j.exec_summary || "",
    remediations: Array.isArray(j.remediations) ? j.remediations.slice(0, 3) : [],
    model: cfg.id,
  });
};
