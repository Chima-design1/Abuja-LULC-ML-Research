from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "outputs"
    / "area_statistics"
    / "LULC_Area_Statistics_Year_Specific.csv"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "change_analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


CLASS_NAMES = [
    "Built-up",
    "Vegetation",
    "Bare land",
    "Water",
    "Cropland",
]


df = pd.read_csv(INPUT_FILE)


area_table = (
    df.pivot(
        index="year",
        columns="class_name",
        values="area_km2",
    )
    .reindex(columns=CLASS_NAMES)
    .sort_index()
)


records = []

years = list(area_table.index)


for i in range(len(years) - 1):

    year1 = years[i]
    year2 = years[i + 1]

    record = {
        "from_year": year1,
        "to_year": year2,
    }

    for class_name in CLASS_NAMES:

        old_area = area_table.loc[
            year1,
            class_name,
        ]

        new_area = area_table.loc[
            year2,
            class_name,
        ]

        record[
            f"{class_name}_change_km2"
        ] = new_area - old_area

        record[
            f"{class_name}_percent_change"
        ] = (
            (new_area - old_area)
            / old_area
            * 100
        )

    records.append(record)


# Add overall 2018 → 2024 change.

year1 = years[0]
year2 = years[-1]

record = {
    "from_year": year1,
    "to_year": year2,
}

for class_name in CLASS_NAMES:

    old_area = area_table.loc[
        year1,
        class_name,
    ]

    new_area = area_table.loc[
        year2,
        class_name,
    ]

    record[
        f"{class_name}_change_km2"
    ] = new_area - old_area

    record[
        f"{class_name}_percent_change"
    ] = (
        (new_area - old_area)
        / old_area
        * 100
    )

records.append(record)


net_change_df = pd.DataFrame(records)


output_file = (
    OUTPUT_DIR
    / "LULC_Net_Changes_Year_Specific.csv"
)

net_change_df.to_csv(
    output_file,
    index=False,
)


print("\n" + "=" * 70)
print("LULC NET AREA CHANGES")
print("=" * 70)


for _, row in net_change_df.iterrows():

    print(
        f"\n{int(row['from_year'])} → "
        f"{int(row['to_year'])}"
    )

    for class_name in CLASS_NAMES:

        change = row[
            f"{class_name}_change_km2"
        ]

        percent = row[
            f"{class_name}_percent_change"
        ]

        sign = "+" if change >= 0 else ""

        print(
            f"  {class_name:<12} "
            f"{sign}{change:.2f} km² "
            f"({sign}{percent:.2f}%)"
        )


print("\n" + "=" * 70)
print("NET CHANGE CALCULATION COMPLETE")
print("=" * 70)

print(
    f"Saved: {output_file}"
)
