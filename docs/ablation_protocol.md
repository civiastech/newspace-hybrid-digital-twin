# Ablation Protocol

Ablations compare grouped runs by a named factor such as modality, augmentation, loss, or fusion strategy.

Required run fields:
- run_id
- task
- metrics
- tags.factor
- tags.variant

Primary outputs:
- ablation summary JSON
- ranked ablation table CSV
- markdown summary
