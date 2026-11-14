(function () {
  var style = document.createElement("style");
  style.textContent = ".lang-switch{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.header .lang-switch a{border:1px solid #d5deea;border-radius:999px;padding:3px 8px;font-size:12px;font-weight:800;color:#142e52;line-height:1.4;text-decoration:none}.header .lang-switch a[aria-current=page]{background:#142e52;color:#fff}.site-header .lang-switch a{border:1px solid #ffffff66;border-radius:999px;padding:3px 8px;font-size:12px;font-weight:800;color:#eaf1f7;line-height:1.4;text-decoration:none}.site-header .lang-switch a[aria-current=page]{background:#fff;color:#102b47}";
  document.head.appendChild(style);

  var parts = location.pathname.split("/").filter(Boolean);
  var lang = parts[0] === "en" || parts[0] === "hi" ? parts.shift() : "ja";
  if (parts[parts.length - 1] === "index.html") parts.pop();
  if (parts.length && /\.html$/.test(parts[parts.length - 1])) {
    parts[parts.length - 1] = parts[parts.length - 1].replace(/\.html$/, "");
  }
  var rest = parts.join("/");

  function hrefFor(target, pathRest) {
    var prefix = target === "ja" ? "" : "/" + target;
    var path = prefix + (pathRest ? "/" + pathRest : "/");
    path = path.replace(/\/{2,}/g, "/");
    if (path.length > 1 && path.endsWith("/")) path = path.slice(0, -1);
    return path || "/";
  }

  document.querySelectorAll("[data-lang-switch] a").forEach(function (link) {
    var target = link.getAttribute("data-lang");
    var alt = document.querySelector('link[rel="alternate"][hreflang="' + target + '"]');
    if (alt) link.href = alt.getAttribute("href");
    else if (rest.indexOf("articles/") === 0) link.href = hrefFor(target, "articles");
    else link.href = hrefFor(target, rest);
    if (target === lang) link.setAttribute("aria-current", "page");
  });

  function send(eventName, extra) {
    var body = JSON.stringify(Object.assign({ event: eventName, path: location.pathname, lang: lang }, extra || {}));
    var blob = new Blob([body], { type: "text/plain;charset=UTF-8" });
    if (navigator.sendBeacon) navigator.sendBeacon("/api/collect", blob);
    else fetch("/api/collect", { method: "POST", body: body, keepalive: true, headers: { "content-type": "text/plain;charset=UTF-8" } }).catch(function () {});
  }

  var refHost = "";
  try { if (document.referrer) refHost = new URL(document.referrer).host; } catch (e) {}
  send("page_view", { ref_host: refHost });

  document.addEventListener("click", function (event) {
    var el = event.target.closest("a,button");
    if (!el) return;
    var href = el.getAttribute("href") || "";
    var target = href || el.getAttribute("aria-label") || (el.textContent || "");
    target = target.replace(/\s+/g, " ").trim().slice(0, 80);
    if (!target) return;
    send("click", { target: target });
  });
})();
