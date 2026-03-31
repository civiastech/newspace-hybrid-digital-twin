CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS aoi (
    aoi_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    case_study_type TEXT NOT NULL,
    target_crs INTEGER NOT NULL,
    time_start TIMESTAMP,
    time_end TIMESTAMP,
    geometry GEOMETRY(MultiPolygon, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS observations (
    observation_id TEXT PRIMARY KEY,
    aoi_id TEXT NOT NULL REFERENCES aoi(aoi_id),
    modality TEXT NOT NULL,
    acquisition_time TIMESTAMP NOT NULL,
    source_uri TEXT NOT NULL,
    checksum TEXT NOT NULL,
    crs_epsg INTEGER,
    footprint GEOMETRY(Geometry, 4326),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    lineage_parent_id TEXT,
    status TEXT NOT NULL DEFAULT 'raw',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS features (
    feature_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    aoi_id TEXT NOT NULL REFERENCES aoi(aoi_id),
    ts TIMESTAMP NOT NULL,
    feature_group TEXT NOT NULL,
    feature_values JSONB NOT NULL,
    source_observation_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    quality_flags JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dataset_samples (
    sample_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    split TEXT NOT NULL,
    task_type TEXT NOT NULL,
    input_uris JSONB NOT NULL DEFAULT '[]'::jsonb,
    label_uri TEXT,
    feature_uri TEXT,
    source_observation_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    model_family TEXT NOT NULL,
    model_version TEXT NOT NULL,
    output_type TEXT NOT NULL,
    prediction_values JSONB NOT NULL,
    confidence DOUBLE PRECISION,
    source_sample_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fusion_outputs (
    fusion_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    optical_score DOUBLE PRECISION,
    sar_score DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION,
    fused_condition_score DOUBLE PRECISION NOT NULL,
    uncertainty_score DOUBLE PRECISION NOT NULL,
    consistency_score DOUBLE PRECISION NOT NULL,
    weighting_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS twin_states (
    state_id TEXT PRIMARY KEY,
    unit_id TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    fused_condition_score DOUBLE PRECISION NOT NULL,
    severity_class TEXT NOT NULL,
    anomaly_score DOUBLE PRECISION NOT NULL,
    uncertainty_score DOUBLE PRECISION NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL,
    priority_rank INTEGER,
    recommended_action TEXT NOT NULL,
    previous_state_id TEXT,
    state_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    stage TEXT NOT NULL,
    config_hash TEXT NOT NULL,
    git_commit TEXT,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    status TEXT NOT NULL,
    output_report_uri TEXT,
    logs_uri TEXT
);
