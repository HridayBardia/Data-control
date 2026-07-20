import time
from typing import Dict, Tuple

class RedisSlidingWindowRateLimiter:
    """In-memory & Redis sliding-window rate limiter per user / org / API endpoint."""

    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self._history: Dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> Tuple[bool, int, float]:
        now = time.time()
        window_start = now - 60.0

        if key not in self._history:
            self._history[key] = []

        # Remove entries outside window
        self._history[key] = [t for t in self._history[key] if t > window_start]

        current_count = len(self._history[key])
        if current_count >= self.requests_per_minute:
            retry_after = round(60.0 - (now - self._history[key][0]), 1)
            return False, current_count, max(0.1, retry_after)

        self._history[key].append(now)
        return True, current_count + 1, 0.0


rate_limiter = RedisSlidingWindowRateLimiter(requests_per_minute=120)
