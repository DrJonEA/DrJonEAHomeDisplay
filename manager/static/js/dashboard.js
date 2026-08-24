// Live dashboard updates: SSE with polling fallback.
(function () {
  const config = window.DECK_CONFIG || {};
  const statusEl = document.getElementById("sse-status");

  function updatePage(data) {
    document.getElementById("last-topic").textContent = data.topic || "None";
    document.getElementById("last-payload").textContent = data.payload || "None";
    document.getElementById("last-layout").textContent = data.layout || "None";

    const widgetBody = document.getElementById("widget-body");
    if (data.widgets && Array.isArray(data.widgets) && data.widgets.length) {
      widgetBody.innerHTML = data.widgets
        .map(
          (widget) =>
            `<tr><td>${widget.type || ""}</td><td>${widget.data || ""}</td></tr>`
        )
        .join("");
    } else {
      widgetBody.innerHTML = '<tr><td colspan="2">No widgets</td></tr>';
    }
  }

  function pollLatest() {
    fetch(config.latestUrl)
      .then((resp) => resp.json())
      .then(updatePage)
      .catch((err) => console.error("Polling error", err));
  }

  if (config.eventsUrl) {
    const eventSource = new EventSource(config.eventsUrl);
    eventSource.onopen = () => {
      statusEl.textContent = "connected";
      statusEl.className = "status-value ok";
    };
    eventSource.onerror = () => {
      statusEl.textContent = "disconnected, retrying...";
      statusEl.className = "status-value warn";
    };
    eventSource.onmessage = (event) => {
      updatePage(JSON.parse(event.data));
    };
  }

  pollLatest();
  setInterval(pollLatest, 10000);
})();
