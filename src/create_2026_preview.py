from pathlib import Path

import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import ListedColormap


ROOT = Path(__file__).resolve().parent.parent

INPUT_MAP = (
    ROOT
    / "outputs"
    / "prediction_2026"
    / "Abuja_LULC_2026_Baseline_Scenario.tif"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "prediction_2026"
    / "preview"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "Abuja_LULC_2026_Baseline_Scenario.png"
)


CLASS_NAMES = [
    "Built-up",
    "Vegetation",
    "Bare land",
    "Water",
    "Cropland",
]


with rasterio.open(INPUT_MAP) as src:

    lulc = src.read(1)

    bounds = src.bounds


masked = lulc.astype(float)

masked[lulc == 255] = float("nan")


cmap = ListedColormap([
    "#d73027",
    "#1a9850",
    "#d9b300",
    "#4575b4",
    "#984ea3",
])


plt.figure(
    figsize=(11, 8)
)

image = plt.imshow(
    masked,
    cmap=cmap,
    vmin=0,
    vmax=4,
)


plt.title(
    "Abuja 2026 Baseline LULC Scenario",
    fontsize=15,
    fontweight="bold",
)

plt.xlabel(
    "Easting / pixel position"
)

plt.ylabel(
    "Northing / pixel position"
)


cbar = plt.colorbar(
    image,
    ticks=range(5),
    fraction=0.035,
    pad=0.03,
)

cbar.ax.set_yticklabels(
    CLASS_NAMES
)

cbar.set_label(
    "Land Use / Land Cover Class"
)


plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


print("=" * 60)
print("2026 PREVIEW CREATED")
print("=" * 60)

print(
    f"Input : {INPUT_MAP}"
)

print(
    f"Output: {OUTPUT_FILE}"
)
