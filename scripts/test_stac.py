import geopandas as gpd
from newspace_twin.ingestion.stac_client import STACClient

# Load AOI
aoi = gpd.read_file("data/raw/aoi/wildfire_case_aoi.geojson")

client = STACClient()

items = client.filter_sentinel2(
    aoi_gdf=aoi,
    start_date="2022-07-01",
    end_date="2022-07-15",
    cloud_cover_max=20,
)

print(f"Found {len(items)} scenes")

for item in items[:3]:
    print(item.id)