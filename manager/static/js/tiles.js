// Click any tile image tagged with data-tile="<display path>" to send it to the Cosmic displays.
(function () {
  const config = window.DECK_CONFIG || {};
  if (!config.showTileUrl) return;

  let toast = null;
  let toastTimer = null;

  function notify(message, isError) {
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "tile-toast";
      toast.setAttribute("role", "status");
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.toggle("error", Boolean(isError));
    toast.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 3000);
  }

  function send(img) {
    const data = img.dataset.tile;
    img.classList.add("sending");
    fetch(config.showTileUrl, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ data }),
    })
      .then((resp) => resp.json().then((body) => ({ ok: resp.ok, body })))
      .then(({ ok, body }) => {
        if (ok) notify("Sent " + body.sent + " to the displays");
        else notify(body.error || "Couldn't send the tile", true);
      })
      .catch(() => notify("Couldn't reach the manager", true))
      .finally(() => img.classList.remove("sending"));
  }

  document.addEventListener("click", (event) => {
    const img = event.target.closest("img[data-tile]");
    if (img) send(img);
  });

  // Make tiles reachable and usable from the keyboard as well.
  document.querySelectorAll("img[data-tile]").forEach((img) => {
    img.tabIndex = 0;
    img.setAttribute("role", "button");
    img.title = "Show " + img.dataset.tile + " on the displays";
    img.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        send(img);
      }
    });
  });
})();
