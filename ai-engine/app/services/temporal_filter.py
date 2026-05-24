"""Multi-frame temporal smoothing — Blueprint v2.0 (5/15 window)."""

from collections import deque
from typing import Deque


class TemporalViolationFilter:
    """
    Confirm violations only when detected in `threshold` of the last `window` frames.
    Eliminates single-frame false positives from motion blur, glare, or partial occlusion.
    """

    def __init__(self, threshold: int = 5, window: int = 15) -> None:
        self.threshold = threshold
        self.window = window
        self._history: dict[str, Deque[bool]] = {}

    def update(self, track_id: str, violation_key: str, detected: bool) -> bool:
        key = f"{track_id}:{violation_key}"
        if key not in self._history:
            self._history[key] = deque(maxlen=self.window)
        self._history[key].append(detected)
        return sum(self._history[key]) >= self.threshold

    def reset(self, track_id: str, violation_key: str) -> None:
        key = f"{track_id}:{violation_key}"
        if key in self._history:
            self._history[key].clear()

    def clear_track(self, track_id: str) -> None:
        stale = [k for k in self._history if k.startswith(f"{track_id}:")]
        for k in stale:
            del self._history[k]
