from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "outputs" / "lulc_maps"
OUTPUT_DIR = ROOT / "outputs" / "area_statistics"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

YEARS = [2018, 2020, 2022, 2024]

CLASS_NAMES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}


records = []


for year in YEARS:

    path = (
        INPUT_DIR
        / f"Abuja_LULC_{year}_year_specific.tif"
    )

    print("=" * 60)
    print(f"PROCESSING {year}")

    with rasterio.open(path) as src:

        data = src.read(1)

        valid = data != 255

        pixel_area_m2 = (
            abs(src.transform.a)
            * abs(src.transform.e)
        )

        pixel_area_km2 = (
            pixel_area_m2 / 1_000_000
        )

        valid_pixels = valid.sum()

        print(
            f"Valid pixels: {valid_pixels:,}"
        )

        for class_code, class_name in CLASS_NAMES.items():

            count = np.sum(
                data[valid] == class_code
            )

            area_km2 = (
                count * pixel_area_km2
            )

            percentage = (
                count
                / valid_pixels
                * 100
            )

            records.append(
                {
                    "year": year,
                    "class_code": class_code,
                    "class_name": class_name,
                    "pixel_count": int(count),
                    "area_km2": area_km2,
                    "percentage": percentage,
                }
            )

            print(
                f"{class_name:<12} "
                f"{area_km2:8.2f} km² "
                f"({percentage:6.2f}%)"
            )


df = pd.DataFrame(records)


output_path = (
    OUTPUT_DIR
    / "LULC_Area_Statistics_Year_Specific.csv"
)

df.to_csv(
    output_path,
    index=False,
)


print("\n" + "=" * 60)
print("AREA STATISTICS COMPLETE")
print("=" * 60)

print(f"Saved: {output_path}")
