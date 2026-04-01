from newspace_twin.twin.temporal import build_temporal_risk_state


def main() -> None:
    previous_geojson = "data/twin/wildfire_case_aoi/risk_layer.geojson"
    current_geojson = "data/twin/wildfire_case_aoi/risk_layer_t2.geojson"
    output_geojson = "data/twin/wildfire_case_aoi/risk_evolution.geojson"

    path = build_temporal_risk_state(
        previous_geojson=previous_geojson,
        current_geojson=current_geojson,
        output_geojson=output_geojson,
    )

    print("Temporal evolution layer created:", path)


if __name__ == "__main__":
    main()