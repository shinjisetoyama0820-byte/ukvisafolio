function tokyoDay(offset) {
  const date = new Date(Date.now() + offset * 86400000);
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tokyo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

export async function onRequestGet(context) {
  const db = context.env.METRICS_DB;
  const headers = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
  if (!db) return Response.json({ ready: false }, { headers });
  const from = tokyoDay(-13);
  try {
    const days = await db.prepare(
      `SELECT day, SUM(count) AS pageviews
       FROM daily_events WHERE event = 'page_view' AND day >= ?1
       GROUP BY day ORDER BY day`
    ).bind(from).all();
    const visitors = await db.prepare(
      `SELECT day, COUNT(*) AS visitors
       FROM daily_visitors WHERE day >= ?1
       GROUP BY day ORDER BY day`
    ).bind(from).all();
    const countries = await db.prepare(
      `SELECT country, COUNT(*) AS visitors
       FROM daily_visitors WHERE day >= ?1
       GROUP BY country ORDER BY visitors DESC LIMIT 20`
    ).bind(from).all();
    const languages = await db.prepare(
      `SELECT lang, SUM(count) AS pageviews
       FROM daily_events WHERE event = 'page_view' AND day >= ?1
       GROUP BY lang ORDER BY pageviews DESC`
    ).bind(from).all();
    const pages = await db.prepare(
      `SELECT path, SUM(count) AS pageviews
       FROM daily_events WHERE event = 'page_view' AND day >= ?1
       GROUP BY path ORDER BY pageviews DESC LIMIT 20`
    ).bind(from).all();
    const clicks = await db.prepare(
      `SELECT target, SUM(count) AS clicks
       FROM daily_events WHERE event = 'click' AND day >= ?1
       GROUP BY target ORDER BY clicks DESC LIMIT 30`
    ).bind(from).all();
    return Response.json({
      ready: true,
      today: tokyoDay(0),
      days: days.results || [],
      visitors: visitors.results || [],
      countries: countries.results || [],
      languages: languages.results || [],
      pages: pages.results || [],
      clicks: clicks.results || [],
    }, { headers });
  } catch (e) {
    return Response.json({ ready: false }, { headers });
  }
}
