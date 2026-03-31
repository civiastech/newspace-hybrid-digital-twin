from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path

import torch


def save_checkpoint(path: str | Path, model: torch.nn.Module, optimizer: torch.optim.Optimizer, cfg, extra: dict | None = None) -> None:
    cfg_payload = asdict(cfg) if is_dataclass(cfg) else cfg
    torch.save({'model_state_dict': model.state_dict(), 'optimizer_state_dict': optimizer.state_dict(), 'config': cfg_payload, 'extra': extra or {}}, path)
