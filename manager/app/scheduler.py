"""Background scheduler that periodically refreshes cached data from external sources.

Add a new source with scheduler.register(name, fetch_fn, interval_seconds); it will
be polled and cached on the shared background thread. Intended for weather now, and
sunrise/sunset and moonrise/moonset lookups later.
"""
import logging
import threading
import time


class CachedSource:
    """A single named source: a fetch function run on an interval, with the last good result cached."""

    def __init__(self, name, fetch_fn, interval_seconds):
        self.name = name
        self.fetch_fn = fetch_fn
        self.interval_seconds = interval_seconds
        self._lock = threading.Lock()
        self._value = None
        self._updated_at = None
        self._error = None

    def is_due(self, now):
        return self._updated_at is None or (now - self._updated_at) >= self.interval_seconds

    def refresh(self, now):
        try:
            result = self.fetch_fn()
        except Exception as exc:
            logging.warning("Scheduled source '%s' fetch failed: %s", self.name, exc)
            with self._lock:
                self._error = str(exc)
            return
        with self._lock:
            self._value = result
            self._updated_at = now
            self._error = None

    def get(self):
        """Return (value, updated_at, error) from the cache; value is None until the first fetch succeeds."""
        with self._lock:
            return self._value, self._updated_at, self._error


class DataScheduler:
    """Runs registered CachedSources on a single background thread, refreshing whichever are due."""

    def __init__(self, poll_interval_seconds=5):
        self.poll_interval_seconds = poll_interval_seconds
        self._sources = {}
        self._stop_event = threading.Event()
        self._thread = None

    def register(self, name, fetch_fn, interval_seconds):
        """Register a data source. Safe to call before the scheduler thread has been started."""
        self._sources[name] = CachedSource(name, fetch_fn, interval_seconds)

    def get(self, name):
        source = self._sources.get(name)
        if source is None:
            return None, None, None
        return source.get()

    def refresh_now(self, name):
        source = self._sources.get(name)
        if source is not None:
            source.refresh(time.time())

    def _run(self):
        while not self._stop_event.is_set():
            now = time.time()
            for source in list(self._sources.values()):
                if source.is_due(now):
                    source.refresh(now)
            self._stop_event.wait(self.poll_interval_seconds)

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
