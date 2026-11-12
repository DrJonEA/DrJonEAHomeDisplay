// Network sweep panel: while a sweep is running, re-fetch the panel fragment every 2s so each
// stage and result appears as it happens. When it finishes, refresh the sensor tile previews.
(function () {
  const config = window.DECK_CONFIG || {};
  const POLL_MS = 2000;

  function body() {
    return document.getElementById("network-sweep-body");
  }

  function isRunning() {
    const el = body();
    return el && el.dataset.running === "true";
  }

  function refreshSensorTiles() {
    const stamp = Date.now();
    document.querySelectorAll("#sensors img").forEach((img) => {
      const url = new URL(img.src, window.location.href);
      url.searchParams.set("t", stamp);
      img.src = url.toString();
    });
  }

  function poll() {
    fetch(config.sweepPanelUrl, { cache: "no-store" })
      .then((resp) => resp.text())
      .then((html) => {
        const el = body();
        if (!el) return;
        el.outerHTML = html;
        if (isRunning()) {
          setTimeout(poll, POLL_MS);
        } else {
          refreshSensorTiles();
        }
      })
      .catch((err) => {
        console.error("Network sweep poll failed", err);
        setTimeout(poll, POLL_MS * 2);
      });
  }

  if (config.sweepPanelUrl && isRunning()) {
    setTimeout(poll, POLL_MS);
  }
})();
