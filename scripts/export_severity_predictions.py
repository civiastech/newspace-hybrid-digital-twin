from pathlib import Path

from newspace_twin.models.severity.export_predictions import export_validation_predictions
from newspace_twin.outputs.prediction_maps import export_prediction_geojson


def main() -> None:
    manifest_csv = "data/manifests/wildfire_case_aoi/dataset_manifest.csv"
    checkpoint_path = "data/reports/checkpoints/severity.pt"
    predictions_csv = "data/predictions/wildfire_case_aoi/severity_val_predictions.csv"
    grid_geojson = "data/manifests/wildfire_case_aoi/analysis_grid.geojson"
    output_geojson = "data/predictions/wildfire_case_aoi/severity_val_predictions.geojson"

    export_validation_predictions(
        manifest_csv=manifest_csv,
        checkpoint_path=checkpoint_path,
        output_csv=predictions_csv,
        device="cpu",
    )

    export_prediction_geojson(
        grid_geojson=grid_geojson,
        predictions_csv=predictions_csv,
        output_geojson=output_geojson,
    )

    print("Prediction CSV:", predictions_csv)
    print("Prediction map:", output_geojson)


if __name__ == "__main__":
    main()