from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_MAP = (
    ROOT
    / "outputs"
    / "lulc_maps"
    / "Abuja_LULC_2024_year_specific.tif"
)

TRANSITION_FILE = (
    ROOT
    / "outputs"
    / "transition_analysis"
    / "transition_matrix_2022_2024.csv"
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

OUTPUT_MAP = (
    OUTPUT_DIR
    / "Abuja_LULC_2026_Baseline_Scenario.tif"
)

PROBABILITY_FILE = (
    OUTPUT_DIR
    / "Transition_Probabilities_2022_2024.csv"
)


# ============================================================
# CLASSES
# ============================================================

CLASSES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}

CLASS_CODES = list(CLASSES.keys())


# ============================================================
# LOAD TRANSITION MATRIX
# ============================================================

transition_df = pd.read_csv(
    TRANSITION_FILE
)

transition_matrix = np.zeros(
    (5, 5),
    dtype=np.float64,
)

for _, row in transition_df.iterrows():

    source = int(row["from_class"])
    target = int(row["to_class"])

    transition_matrix[
        source,
        target
    ] = float(row["pixel_count"])


# ============================================================
# CALCULATE TRANSITION PROBABILITIES
# ============================================================

row_totals = transition_matrix.sum(
    axis=1,
    keepdims=True,
)

transition_probabilities = (
    transition_matrix
    / row_totals
)


# Save probabilities for documentation
probability_df = pd.DataFrame(
    transition_probabilities,
    index=[
        CLASSES[i]
        for i in CLASS_CODES
    ],
    columns=[
        CLASSES[i]
        for i in CLASS_CODES
    ],
)

probability_df.to_csv(
    PROBABILITY_FILE
)

print("\n2022 → 2024 Transition Probabilities")
print("=" * 60)

print(
    probability_df.round(4)
)


# ============================================================
# LOAD 2024 LULC MAP
# ============================================================

with rasterio.open(INPUT_MAP) as src:

    lulc_2024 = src.read(1)

    profile = src.profile.copy()

    nodata = src.nodata

    transform = src.transform

    crs = src.crs

    width = src.width
    height = src.height


valid_mask = np.isin(
    lulc_2024,
    CLASS_CODES,
)

if nodata is not None:

    valid_mask &= (
        lulc_2024 != nodata
    )


# ============================================================
# 2024 CLASS QUANTITIES
# ============================================================

valid_2024 = lulc_2024[
    valid_mask
]

class_counts_2024 = np.array(
    [
        np.sum(valid_2024 == code)
        for code in CLASS_CODES
    ],
    dtype=np.int64,
)


print("\n2024 Class Quantities")
print("=" * 60)

for code, count in zip(
    CLASS_CODES,
    class_counts_2024,
):

    percentage = (
        count
        / len(valid_2024)
        * 100
    )

    print(
        f"{CLASSES[code]:<12} "
        f"{count:>10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# EXPECTED 2026 QUANTITIES
# ============================================================

# Treat the 2024 class distribution as the starting state.
#
# Multiplying the 2024 quantities by the observed
# 2022→2024 transition matrix gives the expected
# destination quantities for the baseline scenario.

expected_counts = (
    class_counts_2024
    @ transition_probabilities
)

expected_counts = np.rint(
    expected_counts
).astype(np.int64)


# Ensure the total remains exactly equal
# to the number of valid pixels.

difference = (
    len(valid_2024)
    - expected_counts.sum()
)

if difference != 0:

    largest_class = np.argmax(
        expected_counts
    )

    expected_counts[
        largest_class
    ] += difference


print("\nExpected 2026 Baseline Quantities")
print("=" * 60)

for code, count in zip(
    CLASS_CODES,
    expected_counts,
):

    percentage = (
        count
        / len(valid_2024)
        * 100
    )

    print(
        f"{CLASSES[code]:<12} "
        f"{count:>10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# SPATIAL ALLOCATION
# ============================================================

# The transition probabilities determine the quantity
# of each 2026 class.
#
# Spatial allocation is based on transition suitability:
# pixels belonging to each 2024 source class are ranked
# according to the relative likelihood of changing into
# each destination class.
#
# A deterministic allocation is then performed so that
# the final 2026 map exactly matches the expected class
# quantities.


prediction_2026 = np.full(
    lulc_2024.shape,
    255,
    dtype=np.uint8,
)


# Start with each pixel retaining its 2024 class.
prediction_2026[
    valid_mask
] = lulc_2024[
    valid_mask
]


# ------------------------------------------------------------
# Calculate required changes
# ------------------------------------------------------------

current_counts = class_counts_2024.copy()

required_change = (
    expected_counts
    - current_counts
)

print("\nRequired Net Class Changes")
print("=" * 60)

for code, change in zip(
    CLASS_CODES,
    required_change,
):

    print(
        f"{CLASSES[code]:<12} "
        f"{change:+,}"
    )


# ============================================================
# BUILD TRANSITION CANDIDATES
# ============================================================

# For each source class, determine which destination
# classes have a higher transition probability than
# retaining the source class.

candidate_changes = []

for source in CLASS_CODES:

    source_pixels = np.argwhere(
        valid_mask
        & (lulc_2024 == source)
    )

    if len(source_pixels) == 0:
        continue

    source_probabilities = (
        transition_probabilities[
            source
        ]
    )

    for destination in CLASS_CODES:

        if destination == source:
            continue

        probability = (
            source_probabilities[
                destination
            ]
        )

        if probability <= 0:
            continue

        # Change score combines destination probability
        # with the source pixel's class relationship.
        #
        # A deterministic spatial ordering is used so
        # results are reproducible.

        for row, col in source_pixels:

            candidate_changes.append(
                (
                    probability,
                    source,
                    destination,
                    row,
                    col,
                )
            )


# ============================================================
# SELECT CHANGES TO MATCH TARGET QUANTITIES
# ============================================================

# Work from the strongest transition probabilities first.

candidate_changes.sort(
    key=lambda x: x[0],
    reverse=True,
)


remaining_gains = {
    code: max(
        int(required_change[code]),
        0,
    )
    for code in CLASS_CODES
}

remaining_losses = {
    code: max(
        int(-required_change[code]),
        0,
    )
    for code in CLASS_CODES
}


changed_pixels = set()

for (
    probability,
    source,
    destination,
    row,
    col,
) in candidate_changes:

    if remaining_gains[destination] <= 0:
        continue

    if remaining_losses[source] <= 0:
        continue

    pixel_id = (
        int(row) * width
        + int(col)
    )

    if pixel_id in changed_pixels:
        continue

    prediction_2026[
        row,
        col
    ] = destination

    changed_pixels.add(
        pixel_id
    )

    remaining_gains[
        destination
    ] -= 1

    remaining_losses[
        source
    ] -= 1

    if all(
        value <= 0
        for value in remaining_gains.values()
    ):
        break


# ============================================================
# FINAL CLASS QUANTITIES
# ============================================================

valid_prediction = prediction_2026[
    valid_mask
]

final_counts = np.array(
    [
        np.sum(
            valid_prediction == code
        )
        for code in CLASS_CODES
    ],
    dtype=np.int64,
)


print("\nFinal 2026 Baseline Map")
print("=" * 60)

for code, count in zip(
    CLASS_CODES,
    final_counts,
):

    percentage = (
        count
        / len(valid_prediction)
        * 100
    )

    print(
        f"{CLASSES[code]:<12} "
        f"{count:>10,} "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# SAVE RASTER
# ============================================================

profile.update(
    dtype="uint8",
    count=1,
    nodata=255,
    compress="lzw",
)

with rasterio.open(
    OUTPUT_MAP,
    "w",
    **profile,
) as dst:

    dst.write(
        prediction_2026,
        1,
    )


# ============================================================
# VALIDATION CHECK
# ============================================================

target_total = expected_counts.sum()
actual_total = final_counts.sum()

print("\nQuantity Check")
print("=" * 60)

print(
    f"Target valid pixels : {target_total:,}"
)

print(
    f"Actual valid pixels : {actual_total:,}"
)

print(
    f"Difference           : "
    f"{actual_total - target_total:+,}"
)


print("\n" + "=" * 60)
print("2026 BASELINE SCENARIO UPDATED")
print("=" * 60)

print(
    f"Raster: {OUTPUT_MAP}"
)

print(
    f"Probabilities: {PROBABILITY_FILE}"
)
