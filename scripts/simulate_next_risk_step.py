from pathlib import Path

import geopandas as gpd
import numpy as np


def main() -> None:
    src = Path("data/twin/wildfire_case_aoi/risk_layer.geojson")
    dst = Path("data/twin/wildfire_case_aoi/risk_layer_t2.geojson")

    gdf = gpd.read_file(src)

    rng = np.random.default_rng(42)

    if "risk_score" not in gdf.columns:
        raise ValueError("risk_score column missing")

    noise = rng.normal(loc=0.03, scale=0.05, size=len(gdf))
    gdf["risk_score"] = np.clip(gdf["risk_score"] + noise, 0.0, 1.0)

    def classify(score: float) -> str:
        if score >= 0.85:
            return "critical"
        if score >= 0.65:
            return "high"
        if score >= 0.40:
            return "medium"
        return "low"

    def priority(score: float) -> int:
        if score >= 0.85:
            return 1
        if score >= 0.65:
            return 2
        if score >= 0.40:
            return 3
        return 4

    gdf["risk_level"] = gdf["risk_score"].apply(classify)
    gdf["priority_rank"] = gdf["risk_score"].apply(priority)

    dst.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(dst, driver="GeoJSON")

    print("Simulated next time step:", dst)
    

if __name__ == "__main__":
    main()