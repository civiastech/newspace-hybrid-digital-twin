from __future__ import annotations

from pathlib import Path

from newspace_twin.features.optical_real import build_optical_wildfire_features


def main() -> None:
    aoi_id = "wildfire_case_aoi"

    pre_stack = Path("data/interim") / aoi_id / "s2_pre.tif"
    post_stack = Path("data/interim") / aoi_id / "s2_post.tif"
    out_dir = Path("data/features") / aoi_id / "optical"

    if not pre_stack.exists():
        raise FileNotFoundError(f"Missing pre stack: {pre_stack}")
    if not post_stack.exists():
        raise FileNotFoundError(f"Missing post stack: {post_stack}")

    outputs = build_optical_wildfire_features(pre_stack, post_stack, out_dir)

    print("Optical wildfire features created:")
    for name, path in outputs.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()