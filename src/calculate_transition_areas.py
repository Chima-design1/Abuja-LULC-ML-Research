from pathlib import Path

import pandas as pd
import rasterio


ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "outputs" / "transition_analysis"
MAP_DIR = ROOT / "outputs" / "lulc_maps"
OUTPUT_DIR = ROOT / "outputs" / "transition_analysis"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PAIRS = [
    (2018, 2020),
    (2020, 2022),
    (2022, 2024),
    (2018, 2024),
]


for year1, year2 in PAIRS:

    print("\n" + "=" * 60)
    print(f"TRANSITION AREAS: {year1} → {year2}")
    print("=" * 60)

    matrix_path = (
        INPUT_DIR
        / f"transition_matrix_{year1}_{year2}.csv"
    )

    df = pd.read_csv(matrix_path)

    map_path = (
        MAP_DIR
        / f"Abuja_LULC_{year1}_year_specific.tif"
    )

    with rasterio.open(map_path) as src:

        pixel_area_m2 = (
            abs(src.transform.a)
            * abs(src.transform.e)
        )

    pixel_area_km2 = (
        pixel_area_m2 / 1_000_000
    )

    df["area_km2"] = (
        df["pixel_count"]
        * pixel_area_km2
    )

    source_totals = (
        df.groupby("from_class")["pixel_count"]
        .sum()
        .to_dict()
    )

    df["source_class_area_km2"] = (
        df["from_class"]
        .map(source_totals)
        * pixel_area_km2
    )

    df["percent_of_source_class"] = (
        df["pixel_count"]
        / df["from_class"].map(source_totals)
        * 100
    )

    output_path = (
        OUTPUT_DIR
        / f"transition_areas_{year1}_{year2}.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        df[
            [
                "from_class_name",
                "to_class_name",
                "pixel_count",
                "area_km2",
                "percent_of_source_class",
            ]
        ].to_string(index=False)
    )

    print(
        f"\nSaved: {output_path}"
    )


print("\n" + "=" * 60)
print("TRANSITION AREA CALCULATION COMPLETE")
print("=" * 60)
