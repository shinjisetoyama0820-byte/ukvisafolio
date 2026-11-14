(function () {
  var style = document.createElement("style");
  style.textContent = ".lang-switch{position:relative}.lang-tab{display:inline-flex;align-items:center;gap:6px;border:1px solid #d5deea;background:#fff;color:#142e52;border-radius:999px;padding:5px 12px;font:inherit;font-size:12px;font-weight:800;line-height:1.4;cursor:pointer}.lang-tab .lang-caret{font-size:10px}.site-header .lang-tab{border-color:#ffffff66;background:transparent;color:#eaf1f7}.lang-menu{position:absolute;top:calc(100% + 8px);right:0;min-width:148px;background:#fff;border:1px solid #e5eaf0;border-radius:12px;box-shadow:0 12px 28px #15284424;padding:6px;z-index:30;display:flex;flex-direction:column}.lang-menu[hidden]{display:none}.lang-menu a{display:block;padding:8px 10px;border-radius:8px;text-decoration:none;color:#142e52;font-size:13px;font-weight:700}.lang-menu a[aria-current=page]{background:#142e52;color:#fff}";
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

  document.querySelectorAll("[data-lang-switch]").forEach(function (box) {
    var links = Array.prototype.slice.call(box.querySelectorAll("a"));
    var current = null;
    links.forEach(function (link) {
      var target = link.getAttribute("data-lang");
      var alt = document.querySelector('link[rel="alternate"][hreflang="' + target + '"]');
      if (alt) link.href = alt.getAttribute("href");
      else if (rest.indexOf("articles/") === 0) link.href = hrefFor(target, "articles");
      else link.href = hrefFor(target, rest);
      if (target === lang) {
        link.setAttribute("aria-current", "page");
        current = link;
      }
    });
    var button = document.createElement("button");
    button.type = "button";
    button.className = "lang-tab";
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-haspopup", "true");
    button.innerHTML = (current ? current.textContent : "Language") + '<span class="lang-caret" aria-hidden="true">▾</span>';
    var menu = document.createElement("div");
    menu.className = "lang-menu";
    menu.hidden = true;
    links.forEach(function (link) { menu.appendChild(link); });
    box.replaceChildren(button, menu);
    function closeMenu() {
      menu.hidden = true;
      button.setAttribute("aria-expanded", "false");
    }
    button.addEventListener("click", function (event) {
      event.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      button.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", closeMenu);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
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
