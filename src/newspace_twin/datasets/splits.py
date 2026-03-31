from __future__ import annotations

import random
from collections.abc import Iterable


def assign_splits(unit_ids: Iterable[str], *, train: float, val: float, test: float, seed: int) -> dict[str, str]:
    if abs((train + val + test) - 1.0) > 1e-6:
        raise ValueError('Split proportions must sum to 1.0')
    ids = sorted(set(unit_ids))
    rng = random.Random(seed)
    rng.shuffle(ids)

    total = len(ids)
    train_n = int(total * train)
    val_n = int(total * val)
    test_n = total - train_n - val_n

    mapping: dict[str, str] = {}
    for idx, unit_id in enumerate(ids):
        if idx < train_n:
            mapping[unit_id] = 'train'
        elif idx < train_n + val_n:
            mapping[unit_id] = 'val'
        else:
            mapping[unit_id] = 'test'
    if test_n == 0 and total > 0:
        mapping[ids[-1]] = 'test'
    return mapping
