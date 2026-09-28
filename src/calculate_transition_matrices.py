from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "outputs" / "lulc_maps"
OUTPUT_DIR = ROOT / "outputs" / "transition_analysis"

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


def load_map(year):
    path = (
        INPUT_DIR
        / f"Abuja_LULC_{year}_year_specific.tif"
    )

    with rasterio.open(path) as src:
        data = src.read(1)

    return data


def calculate_transition(year1, year2):

    map1 = load_map(year1)
    map2 = load_map(year2)

    valid = (
        (map1 != 255)
        & (map2 != 255)
    )

    from_values = map1[valid]
    to_values = map2[valid]

    matrix = np.zeros(
        (5, 5),
        dtype=np.int64,
    )

    for from_class in range(5):

        for to_class in range(5):

            matrix[
                from_class,
                to_class,
            ] = np.sum(
                (from_values == from_class)
                & (to_values == to_class)
            )

    return matrix


def save_transition_matrix(
    matrix,
    year1,
    year2,
):

    rows = []

    for from_class in range(5):

        for to_class in range(5):

            rows.append(
                {
                    "from_class": from_class,
                    "from_class_name": CLASS_NAMES[
                        from_class
                    ],
                    "to_class": to_class,
                    "to_class_name": CLASS_NAMES[
                        to_class
                    ],
                    "pixel_count": int(
                        matrix[
                            from_class,
                            to_class,
                        ]
                    ),
                }
            )

    df = pd.DataFrame(rows)

    output_path = (
        OUTPUT_DIR
        / f"transition_matrix_{year1}_{year2}.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    return df


pairs = [
    (2018, 2020),
    (2020, 2022),
    (2022, 2024),
    (2018, 2024),
]


for year1, year2 in pairs:

    print("\n" + "=" * 60)
    print(
        f"TRANSITION ANALYSIS: "
        f"{year1} → {year2}"
    )
    print("=" * 60)

    matrix = calculate_transition(
        year1,
        year2,
    )

    df = save_transition_matrix(
        matrix,
        year1,
        year2,
    )

    print("\nTransition matrix (pixels):")

    matrix_df = pd.DataFrame(
        matrix,
        index=[
            CLASS_NAMES[i]
            for i in range(5)
        ],
        columns=[
            CLASS_NAMES[i]
            for i in range(5)
        ],
    )

    print(matrix_df)

    print(
        f"\nSaved: "
        f"transition_matrix_{year1}_{year2}.csv"
    )


print("\n" + "=" * 60)
print("TRANSITION ANALYSIS COMPLETE")
print("=" * 60)

print(
    f"Outputs: {OUTPUT_DIR}"
)
