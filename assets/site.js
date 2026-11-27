(function () {
  var globe = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 14 14'%3E%3Cg fill='none' stroke='%23999' stroke-width='1'%3E%3Ccircle cx='7' cy='7' r='6'/%3E%3Cellipse cx='7' cy='7' rx='2.6' ry='6'/%3E%3Cline x1='1' y1='7' x2='13' y2='7'/%3E%3C/g%3E%3C/svg%3E";
  var chev = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath fill='none' stroke='%23999' stroke-width='1.5' d='M1 1l4 4 4-4'/%3E%3C/svg%3E";
  var globeLight = globe.replace("%23999", "%23eaf1f7");
  var chevLight = chev.replace("%23999", "%23eaf1f7");
  var style = document.createElement("style");
  style.textContent = ".lang-select{appearance:none;-webkit-appearance:none;-moz-appearance:none;background-color:transparent;background-image:url(\"" + globe + "\"),url(\"" + chev + "\");background-repeat:no-repeat,no-repeat;background-position:left 6px center,right 6px center;border:1px solid #d7dee8;border-radius:8px;padding:3px 20px 3px 24px;font-size:12px;font-weight:500;color:#5c6b80;cursor:pointer;font-family:inherit;line-height:1.4;flex-shrink:0}.site-header .lang-select{border-color:#ffffff66;color:#eaf1f7;background-image:url(\"" + globeLight + "\"),url(\"" + chevLight + "\")}";
  document.head.appendChild(style);

  var parts = location.pathname.split("/").filter(Boolean);
  var lang = parts[0] === "en" || parts[0] === "hi" || parts[0] === "zh-tw" || parts[0] === "ko" ? parts.shift() : "ja";
  if (parts[parts.length - 1] === "index.html") parts.pop();
  if (parts.length && /\.html$/.test(parts[parts.length - 1])) {
    parts[parts.length - 1] = parts[parts.length - 1].replace(/\.html$/, "");
  }
  var rest = parts.join("/");
  var labels = [["ja", "日本語"], ["en", "English"], ["hi", "हिन्दी"], ["zh-tw", "繁體中文"], ["ko", "한국어"]];

  function hrefFor(target, pathRest) {
    var prefix = target === "ja" ? "" : "/" + target;
    var path = prefix + (pathRest ? "/" + pathRest : "/");
    path = path.replace(/\/{2,}/g, "/");
    if (path.length > 1 && path.endsWith("/")) path = path.slice(0, -1);
    return path || "/";
  }

  function destination(target) {
    var hreflang = target === "zh-tw" ? "zh-Hant" : target;
    var alt = document.querySelector('link[rel="alternate"][hreflang="' + hreflang + '"]');
    if (alt) return alt.getAttribute("href");
    // A translation may not be published yet. Never link to a missing article.
    if (target === "ko") return hrefFor(target, !rest ? "" : rest === "visa-news" ? "visa-news.html" : "articles.html");
    if (rest.indexOf("articles/") === 0) return hrefFor(target, "articles.html");
    return hrefFor(target, rest);
  }

  function fill(select) {
    var chosen = lang;
    select.setAttribute("aria-label", "Change language");
    select.innerHTML = "";
    labels.forEach(function (row) {
      var option = document.createElement("option");
      option.value = destination(row[0]);
      option.textContent = row[1];
      if (row[0] === chosen) option.selected = true;
      select.appendChild(option);
    });
    select.onchange = function () {
      if (select.value && select.value !== location.pathname && select.value !== location.href) location.href = select.value;
    };
  }

  document.querySelectorAll("[data-lang-select], [data-lang-switch]").forEach(function (box) {
    var select = box.tagName === "SELECT" ? box : box.querySelector("select");
    if (!select) {
      select = document.createElement("select");
      select.className = "lang-select";
      box.replaceChildren(select);
    }
    select.classList.add("lang-select");
    fill(select);
  });

  function send(eventName, extra) {
    try { if (localStorage.getItem("ukvf-nocount") === "1") return; } catch (e) { return; }
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
