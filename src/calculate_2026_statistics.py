from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


ROOT = Path(__file__).resolve().parent.parent

MAP_2024 = (
    ROOT
    / "outputs"
    / "lulc_maps"
    / "Abuja_LULC_2024_year_specific.tif"
)

MAP_2026 = (
    ROOT
    / "outputs"
    / "prediction_2026"
    / "Abuja_LULC_2026_Baseline_Scenario.tif"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "prediction_2026"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

STATS_FILE = (
    OUTPUT_DIR
    / "LULC_Area_Statistics_2024_2026_Baseline.csv"
)

COMPARISON_FILE = (
    OUTPUT_DIR
    / "LULC_2024_vs_2026_Baseline_Comparison.csv"
)


CLASSES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}


# ============================================================
# READ RASTERS
# ============================================================

with rasterio.open(MAP_2024) as src:
    lulc_2024 = src.read(1)
    resolution = src.res
    pixel_area_m2 = abs(
        resolution[0] * resolution[1]
    )

with rasterio.open(MAP_2026) as src:
    lulc_2026 = src.read(1)


# ============================================================
# VALID MASK
# ============================================================

valid_mask = (
    np.isin(lulc_2024, list(CLASSES))
    &
    np.isin(lulc_2026, list(CLASSES))
)


total_pixels = np.sum(valid_mask)

pixel_area_km2 = (
    pixel_area_m2 / 1_000_000
)


# ============================================================
# CALCULATE STATISTICS
# ============================================================

records = []

for code, name in CLASSES.items():

    count_2024 = np.sum(
        valid_mask
        & (lulc_2024 == code)
    )

    count_2026 = np.sum(
        valid_mask
        & (lulc_2026 == code)
    )

    area_2024 = (
        count_2024
        * pixel_area_km2
    )

    area_2026 = (
        count_2026
        * pixel_area_km2
    )

    percentage_2024 = (
        count_2024
        / total_pixels
        * 100
    )

    percentage_2026 = (
        count_2026
        / total_pixels
        * 100
    )

    net_change = (
        area_2026
        - area_2024
    )

    percentage_point_change = (
        percentage_2026
        - percentage_2024
    )

    records.append(
        {
            "class_code": code,
            "class_name": name,
            "pixels_2024": count_2024,
            "area_2024_km2": area_2024,
            "percentage_2024": percentage_2024,
            "pixels_2026_baseline": count_2026,
            "area_2026_baseline_km2": area_2026,
            "percentage_2026_baseline": percentage_2026,
            "net_change_km2": net_change,
            "percentage_point_change": percentage_point_change,
        }
    )


df = pd.DataFrame(records)


# ============================================================
# SAVE STATISTICS
# ============================================================

df.to_csv(
    STATS_FILE,
    index=False,
)


# ============================================================
# COMPARISON TABLE
# ============================================================

comparison = df[
    [
        "class_name",
        "area_2024_km2",
        "area_2026_baseline_km2",
        "net_change_km2",
        "percentage_2024",
        "percentage_2026_baseline",
        "percentage_point_change",
    ]
].copy()


comparison.to_csv(
    COMPARISON_FILE,
    index=False,
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 75)
print("2024 → 2026 BASELINE AREA COMPARISON")
print("=" * 75)

for _, row in comparison.iterrows():

    print(
        f"{row['class_name']:<12} | "
        f"2024: {row['area_2024_km2']:>8.2f} km² "
        f"({row['percentage_2024']:>6.2f}%) | "
        f"2026: {row['area_2026_baseline_km2']:>8.2f} km² "
        f"({row['percentage_2026_baseline']:>6.2f}%) | "
        f"Change: {row['net_change_km2']:>+8.2f} km²"
    )


print("\n" + "=" * 75)
print("FILES CREATED")
print("=" * 75)

print(
    f"Statistics:\n{STATS_FILE}"
)

print(
    f"\nComparison:\n{COMPARISON_FILE}"
)

print(
    f"\nValid pixels: {total_pixels:,}"
)

print(
    f"Pixel area: {pixel_area_km2:.6f} km²"
)
