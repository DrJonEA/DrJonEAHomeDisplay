"""Background scheduler that refreshes cached data from external sources on a cron-style schedule.

Add a new source with scheduler.register(name, fetch_fn, schedule_minutes), where
schedule_minutes is a list of minutes-past-the-hour (e.g. [0, 15, 30, 45]) on which to
run; it will be polled and cached on the shared background thread. Minutes are evaluated
in UTC, which only matters for timezones with a non-whole-hour UTC offset.
"""
import logging
import threading
import time


def _current_slot(now, schedule_minutes):
    """Return a unique (y, m, d, h, minute) tuple if `now`'s minute is scheduled, else None."""
    t = time.gmtime(now)
    if t.tm_min not in schedule_minutes:
        return None
    return (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min)


class CachedSource:
    """A single named source: a fetch function run on a cron-style minute schedule, with the last good result cached."""

    def __init__(self, name, fetch_fn, schedule_minutes):
        self.name = name
        self.fetch_fn = fetch_fn
        self.schedule_minutes = sorted({m % 60 for m in schedule_minutes})
        self._lock = threading.Lock()
        self._value = None
        self._updated_at = None
        self._error = None
        self._last_slot = None

    def is_due(self, now):
        if self._updated_at is None:
            return True  # first run happens immediately, regardless of schedule
        return _current_slot(now, self.schedule_minutes) not in (None, self._last_slot)

    def refresh(self, now):
        slot = _current_slot(now, self.schedule_minutes)
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
        if slot is not None:
            self._last_slot = slot

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

    def register(self, name, fetch_fn, schedule_minutes):
        """Register a data source. Safe to call before the scheduler thread has been started."""
        self._sources[name] = CachedSource(name, fetch_fn, schedule_minutes)

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
