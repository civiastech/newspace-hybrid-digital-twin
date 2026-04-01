from newspace_twin.twin.alerts import build_alert_layer


def main() -> None:
    input_geojson = "data/twin/wildfire_case_aoi/risk_evolution.geojson"
    output_geojson = "data/twin/wildfire_case_aoi/alert_layer.geojson"

    path = build_alert_layer(input_geojson, output_geojson)
    print("Alert layer created:", path)


if __name__ == "__main__":
    main()