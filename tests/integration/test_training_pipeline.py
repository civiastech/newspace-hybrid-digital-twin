from __future__ import annotations

from pathlib import Path

from tests.fixtures.build_training_fixture import build_training_fixture

from newspace_twin.datasets.loaders import ClassificationTileDataset, SegmentationTileDataset
from newspace_twin.models.anomaly.train import train_anomaly_model
from newspace_twin.models.segmentation.train import train_segmentation
from newspace_twin.models.severity.train import train_severity_classifier
from newspace_twin.training.engine import TrainConfig


def test_dataset_loaders_and_training_step(tmp_path: Path) -> None:
    manifest, features = build_training_fixture(tmp_path)
    seg_ds = SegmentationTileDataset(manifest, split='train')
    clf_ds = ClassificationTileDataset(manifest, split='train')
    assert len(seg_ds) == 8
    assert len(clf_ds) == 8
    cfg = TrainConfig(epochs=1, batch_size=2, learning_rate=1e-3, weight_decay=1e-4, device='cpu')
    seg_result = train_segmentation(manifest, tmp_path / 'ckpts', cfg)
    clf_result = train_severity_classifier(manifest, tmp_path / 'ckpts', cfg)
    ano_result = train_anomaly_model(features, tmp_path / 'ckpts', cfg)
    assert Path(seg_result['checkpoint']).exists()
    assert Path(clf_result['checkpoint']).exists()
    assert Path(ano_result['checkpoint']).exists()
    assert 'dice' in seg_result['metrics']
    assert 'macro_f1' in clf_result['metrics']
    assert 'mean_reconstruction_error' in ano_result['metrics']
