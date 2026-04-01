from newspace_twin.twin.risk_from_predictions import build_risk_layer_from_predictions


def main():
    prediction_geojson = "data/predictions/wildfire_case_aoi/severity_val_predictions.geojson"
    output_geojson = "data/twin/wildfire_case_aoi/risk_layer.geojson"

    path = build_risk_layer_from_predictions(
        prediction_geojson=prediction_geojson,
        output_geojson=output_geojson,
    )

    print("Risk layer created:", path)


if __name__ == "__main__":
    main()