from __future__ import annotations

import numpy as np
import pandas as pd


def ndvi(nir: np.ndarray, red: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return (nir - red) / (nir + red + eps)


def nbr(nir: np.ndarray, swir: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return (nir - swir) / (nir + swir + eps)


def ndwi(green: np.ndarray, nir: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return (green - nir) / (green + nir + eps)


def sar_ratio(vv: np.ndarray, vh: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return vv / (vh + eps)


def summarize_sensor_csv(df: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}

    if "temperature_c" in df.columns:
        out["temp_mean"] = float(df["temperature_c"].mean())
        out["temp_max"] = float(df["temperature_c"].max())

    if "humidity_pct" in df.columns:
        out["humidity_mean"] = float(df["humidity_pct"].mean())
        out["humidity_min"] = float(df["humidity_pct"].min())

    if "smoke_ppm" in df.columns:
        out["smoke_mean"] = float(df["smoke_ppm"].mean())
        out["smoke_max"] = float(df["smoke_ppm"].max())

    if "wind_mps" in df.columns:
        out["wind_mean"] = float(df["wind_mps"].mean())
        out["wind_max"] = float(df["wind_mps"].max())

    return out


def build_optical_feature_stack(
    s2_pre_path: str,
    s2_post_path: str,
) -> np.ndarray:
    pre = np.load(s2_pre_path)
    post = np.load(s2_post_path)

    ndvi_pre = ndvi(pre["nir"], pre["red"])
    ndvi_post = ndvi(post["nir"], post["red"])

    nbr_pre = nbr(pre["nir"], pre["swir"])
    nbr_post = nbr(post["nir"], post["swir"])

    ndwi_pre = ndwi(pre["green"], pre["nir"])
    ndwi_post = ndwi(post["green"], post["nir"])

    d_ndvi = ndvi_post - ndvi_pre
    d_nbr = nbr_post - nbr_pre
    d_ndwi = ndwi_post - ndwi_pre

    stack = np.stack(
        [
            ndvi_pre,
            ndvi_post,
            nbr_pre,
            nbr_post,
            ndwi_pre,
            ndwi_post,
            d_ndvi,
            d_nbr,
            d_ndwi,
        ],
        axis=0,
    )
    return stack.astype(np.float32)


def build_sar_feature_stack(
    s1_pre_path: str,
    s1_post_path: str,
) -> np.ndarray:
    pre = np.load(s1_pre_path)
    post = np.load(s1_post_path)

    vv_pre = pre["vv"]
    vh_pre = pre["vh"]
    vv_post = post["vv"]
    vh_post = post["vh"]

    ratio_pre = sar_ratio(vv_pre, vh_pre)
    ratio_post = sar_ratio(vv_post, vh_post)

    d_vv = vv_post - vv_pre
    d_vh = vh_post - vh_pre
    d_ratio = ratio_post - ratio_pre

    stack = np.stack(
        [
            vv_pre,
            vh_pre,
            vv_post,
            vh_post,
            ratio_pre,
            ratio_post,
            d_vv,
            d_vh,
            d_ratio,
        ],
        axis=0,
    )
    return stack.astype(np.float32)