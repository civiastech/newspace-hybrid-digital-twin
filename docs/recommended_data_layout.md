# Recommended Data Layout

Extract this pack into your repository root.

Expected result:
- data/raw/aoi/wildfire_case_aoi.geojson
- data/raw/wildfire_case_aoi/sentinel2/
- data/raw/wildfire_case_aoi/sentinel1/
- data/raw/wildfire_case_aoi/uav/
- data/raw/wildfire_case_aoi/sensors/
- data/raw/wildfire_case_aoi/vectors/
- data/labels/wildfire_case_aoi/

## Intent
This dataset is designed to be:
- realistic enough for pipeline debugging
- coherent across modalities
- useful for feature testing
- useful for fusion logic testing
- useful for digital twin state updates

## Limitation
It is synthetic and must not be used for final scientific claims.