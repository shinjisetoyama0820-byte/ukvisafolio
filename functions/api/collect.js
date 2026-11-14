const EVENTS = new Set(["page_view", "click"]);

function tokyoDay() {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

async function sha(value) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function ensure(db) {
  await db.prepare(`CREATE TABLE IF NOT EXISTS daily_events (
    day TEXT NOT NULL,
    event TEXT NOT NULL,
    path TEXT NOT NULL,
    country TEXT NOT NULL,
    lang TEXT NOT NULL,
    target TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (day, event, path, country, lang, target)
  )`).run();
  await db.prepare(`CREATE TABLE IF NOT EXISTS daily_visitors (
    day TEXT NOT NULL,
    visitor_hash TEXT NOT NULL,
    country TEXT NOT NULL,
    lang TEXT NOT NULL,
    PRIMARY KEY (day, visitor_hash)
  )`).run();
}

function cleanTarget(value) {
  const raw = String(value || "").replace(/\s+/g, " ").trim().slice(0, 80);
  try {
    const url = new URL(raw, "https://ukvisafolio.com");
    if (url.hostname === "stratovisa.com" || url.hostname.endsWith(".stratovisa.com")) {
      const ref = url.searchParams.get("ref");
      return url.origin + url.pathname + (ref ? "?ref=" + ref : "");
    }
    if (/^https?:/i.test(raw)) return url.origin + url.pathname;
  } catch (e) {}
  return raw;
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!env.METRICS_DB) return new Response(null, { status: 204 });
  const ua = request.headers.get("user-agent") || "";
  if (/bot|spider|crawler|preview|headless|facebookexternalhit|slackbot|whatsapp|curl\//i.test(ua)) {
    return new Response(null, { status: 204 });
  }
  let payload = {};
  try {
    const text = await request.text();
    if (!text || text.length > 2000) return new Response(null, { status: 204 });
    payload = JSON.parse(text);
  } catch (e) {
    return new Response(null, { status: 204 });
  }
  const event = String(payload.event || "");
  if (!EVENTS.has(event)) return new Response(null, { status: 204 });
  let path = String(payload.path || "/").split("?")[0].slice(0, 180);
  if (!path.startsWith("/")) path = "/";
  const lang = ["ja", "en", "hi", "zh-tw"].includes(payload.lang) ? payload.lang : "ja";
  const target = event === "click" ? cleanTarget(payload.target) : String(payload.ref_host || "").slice(0, 80);
  const country = (request.headers.get("CF-IPCountry") || "ZZ").replace(/[^A-Za-z]/g, "").slice(0, 2) || "ZZ";
  const day = tokyoDay();
  try {
    await ensure(env.METRICS_DB);
    await env.METRICS_DB.prepare(
      `INSERT INTO daily_events (day, event, path, country, lang, target, count)
       VALUES (?1, ?2, ?3, ?4, ?5, ?6, 1)
       ON CONFLICT(day, event, path, country, lang, target)
       DO UPDATE SET count = count + 1`
    ).bind(day, event, path, country, lang, target).run();
    if (event === "page_view") {
      const ip = request.headers.get("CF-Connecting-IP") || "";
      const hash = (await sha(day + "|" + ip + "|" + ua.slice(0, 120))).slice(0, 32);
      await env.METRICS_DB.prepare(
        `INSERT OR IGNORE INTO daily_visitors (day, visitor_hash, country, lang) VALUES (?1, ?2, ?3, ?4)`
      ).bind(day, hash, country, lang).run();
    }
  } catch (e) {
    return new Response(null, { status: 204 });
  }
  return new Response(null, { status: 204, headers: { "cache-control": "no-store" } });
}
