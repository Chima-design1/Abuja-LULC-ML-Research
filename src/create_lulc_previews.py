from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio


ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "outputs" / "lulc_maps"
OUTPUT_DIR = ROOT / "outputs" / "lulc_previews"

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


for year in YEARS:

    input_path = (
        INPUT_DIR
        / f"Abuja_LULC_{year}_year_specific.tif"
    )

    output_path = (
        OUTPUT_DIR
        / f"Abuja_LULC_{year}_year_specific.png"
    )

    print("=" * 60)
    print(f"Creating preview: {year}")

    with rasterio.open(input_path) as src:

        lulc = src.read(1)

    display = lulc.astype(float)

    display[display == 255] = np.nan

    plt.figure(figsize=(10, 8))

    plt.imshow(
        display,
        vmin=0,
        vmax=4,
        interpolation="nearest",
    )

    plt.title(
        f"Abuja LULC {year} - Year-Specific Classification"
    )

    colorbar = plt.colorbar(
        ticks=[0, 1, 2, 3, 4]
    )

    colorbar.ax.set_yticklabels(
        [
            CLASS_NAMES[0],
            CLASS_NAMES[1],
            CLASS_NAMES[2],
            CLASS_NAMES[3],
            CLASS_NAMES[4],
        ]
    )

    plt.axis("off")
    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Saved: {output_path}")


print("\n" + "=" * 60)
print("PREVIEW GENERATION COMPLETE")
print("=" * 60)
