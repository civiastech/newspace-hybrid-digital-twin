from typing import List, Dict, Optional
from datetime import datetime
import logging

from pystac_client import Client
from shapely.geometry import mapping
import geopandas as gpd

logger = logging.getLogger(__name__)


class STACClient:
    """
    Generic STAC client for querying Earth Observation datasets.

    Supports:
    - Sentinel-2 (L2A)
    - Sentinel-1 (GRD)

    Default endpoint: Microsoft Planetary Computer (stable, free)
    """

    DEFAULT_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

    def __init__(self, stac_url: Optional[str] = None):
        self.stac_url = stac_url or self.DEFAULT_URL
        self.client = Client.open(self.stac_url)

        logger.info(f"STAC client initialized: {self.stac_url}")

    def search(
        self,
        aoi_gdf: gpd.GeoDataFrame,
        collections: List[str],
        start_date: str,
        end_date: str,
        query: Optional[Dict] = None,
        max_items: int = 50,
    ):
        """
        Search STAC catalog.

        Args:
            aoi_gdf: GeoDataFrame (AOI)
            collections: e.g. ["sentinel-2-l2a"]
            start_date: "YYYY-MM-DD"
            end_date: "YYYY-MM-DD"
            query: additional filters (e.g. cloud cover)
            max_items: limit results

        Returns:
            list of STAC items
        """

        geometry = mapping(aoi_gdf.to_crs(4326).geometry.unary_union)

        datetime_range = f"{start_date}/{end_date}"

        search = self.client.search(
            collections=collections,
            intersects=geometry,
            datetime=datetime_range,
            query=query or {},
            max_items=max_items,
        )

        items = list(search.get_items())

        logger.info(f"Found {len(items)} STAC items")

        return items

    def extract_metadata(self, items) -> List[Dict]:
        """
        Extract structured metadata for registry/provenance.
        """

        metadata = []

        for item in items:
            props = item.properties

            record = {
                "scene_id": item.id,
                "datetime": props.get("datetime"),
                "platform": props.get("platform"),
                "cloud_cover": props.get("eo:cloud_cover"),
                "bbox": item.bbox,
                "collection": item.collection_id,
            }

            metadata.append(record)

        return metadata

    def filter_sentinel2(
        self,
        aoi_gdf: gpd.GeoDataFrame,
        start_date: str,
        end_date: str,
        cloud_cover_max: float = 20,
        max_items: int = 20,
    ):
        """
        Sentinel-2 L2A search with cloud filtering.
        """

        return self.search(
            aoi_gdf=aoi_gdf,
            collections=["sentinel-2-l2a"],
            start_date=start_date,
            end_date=end_date,
            query={"eo:cloud_cover": {"lt": cloud_cover_max}},
            max_items=max_items,
        )

    def filter_sentinel1(
        self,
        aoi_gdf: gpd.GeoDataFrame,
        start_date: str,
        end_date: str,
        max_items: int = 20,
    ):
        """
        Sentinel-1 GRD search (VV/VH).
        """

        return self.search(
            aoi_gdf=aoi_gdf,
            collections=["sentinel-1-grd"],
            start_date=start_date,
            end_date=end_date,
            query={},
            max_items=max_items,
        )

    def get_asset_urls(self, item) -> Dict[str, str]:
        """
        Extract usable asset URLs (bands).

        Returns:
            dict of band_name -> URL
        """

        assets = item.assets

        band_urls = {}

        for key, asset in assets.items():
            if asset.href:
                band_urls[key] = asset.href

        return band_urls