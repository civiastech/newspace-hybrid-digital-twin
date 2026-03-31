from __future__ import annotations

from datetime import datetime
import math


def exponential_decay(current_time: datetime, observation_time: datetime, tau_days: float = 10.0) -> float:
    delta_days = max(0.0, (current_time - observation_time).total_seconds() / 86400.0)
    return float(math.exp(-delta_days / tau_days))
