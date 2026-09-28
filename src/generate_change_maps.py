from pathlib import Path

import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "outputs" / "lulc_maps"
OUTPUT_DIR = ROOT / "outputs" / "change_maps"
PREVIEW_DIR = ROOT / "outputs" / "change_map_previews"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)


CLASS_NAMES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}


PAIRS = [
    (2018, 2020),
    (2020, 2022),
    (2022, 2024),
    (2018, 2024),
]


def load_map(year):

    path = (
        INPUT_DIR
        / f"Abuja_LULC_{year}_year_specific.tif"
    )

    with rasterio.open(path) as src:

        data = src.read(1)
        profile = src.profile.copy()

    return data, profile


def create_change_map(year1, year2):

    print("\n" + "=" * 60)
    print(f"CHANGE MAP: {year1} → {year2}")
    print("=" * 60)

    map1, profile1 = load_map(year1)
    map2, profile2 = load_map(year2)

    if map1.shape != map2.shape:

        raise ValueError(
            f"Grid mismatch: "
            f"{year1}={map1.shape}, "
            f"{year2}={map2.shape}"
        )

    valid = (
        (map1 != 255)
        & (map2 != 255)
    )

    changed = (
        valid
        & (map1 != map2)
    )

    unchanged = (
        valid
        & (map1 == map2)
    )

    # Encode each transition:
    #
    # code = 1 + (from_class * 5) + to_class
    #
    # 0   = unchanged
    # 1-25 = transitions
    # 255 = masked

    change = np.full(
        map1.shape,
        255,
        dtype=np.uint8,
    )

    change[unchanged] = 0

    from_class = map1[changed]
    to_class = map2[changed]

    transition_codes = (
        1
        + (from_class * 5)
        + to_class
    )

    change[changed] = (
        transition_codes.astype(np.uint8)
    )

    output_path = (
        OUTPUT_DIR
        / f"Abuja_LULC_Change_{year1}_{year2}.tif"
    )

    profile1.update(
        count=1,
        dtype="uint8",
        nodata=255,
        compress="lzw",
    )

    with rasterio.open(
        output_path,
        "w",
        **profile1,
    ) as dst:

        dst.write(change, 1)

        dst.set_band_description(
            1,
            f"LULC change {year1}-{year2}",
        )

    print(
        f"Valid pixels: {valid.sum():,}"
    )

    print(
        f"Unchanged pixels: "
        f"{unchanged.sum():,}"
    )

    print(
        f"Changed pixels: "
        f"{changed.sum():,}"
    )

    if valid.sum() > 0:

        change_percentage = (
            changed.sum()
            / valid.sum()
            * 100
        )

        print(
            f"Changed area: "
            f"{change_percentage:.2f}%"
        )

    print(
        f"Saved: {output_path}"
    )

    # --------------------------------------------------
    # Print transition summary
    # --------------------------------------------------

    print("\nMajor transitions:")

    transition_records = []

    for from_cls in range(5):

        for to_cls in range(5):

            if from_cls == to_cls:
                continue

            count = np.sum(
                (map1 == from_cls)
                & (map2 == to_cls)
                & valid
            )

            if count > 0:

                transition_records.append(
                    (
                        count,
                        from_cls,
                        to_cls,
                    )
                )

    transition_records.sort(
        reverse=True
    )

    for count, from_cls, to_cls in (
        transition_records[:10]
    ):

        print(
            f"  {CLASS_NAMES[from_cls]}"
            f" → "
            f"{CLASS_NAMES[to_cls]}"
            f": {count:,} pixels"
        )

    # --------------------------------------------------
    # Preview
    # --------------------------------------------------

    preview = change.astype(float)

    preview[preview == 255] = np.nan

    # Unchanged = transparent/white.
    # Changed transitions receive categorical colors.

    plt.figure(
        figsize=(11, 8)
    )

    plt.imshow(
        preview,
        interpolation="nearest",
        cmap="tab20",
        vmin=0,
        vmax=25,
    )

    plt.title(
        f"Abuja LULC Change: "
        f"{year1} → {year2}"
    )

    plt.axis("off")

    plt.tight_layout()

    preview_path = (
        PREVIEW_DIR
        / f"Abuja_LULC_Change_{year1}_{year2}.png"
    )

    plt.savefig(
        preview_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Preview: {preview_path}"
    )


for year1, year2 in PAIRS:

    create_change_map(
        year1,
        year2,
    )


print("\n" + "=" * 60)
print("CHANGE MAP GENERATION COMPLETE")
print("=" * 60)

print(
    f"Maps: {OUTPUT_DIR}"
)

print(
    f"Previews: {PREVIEW_DIR}"
)
