import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling


ROOT = Path(__file__).resolve().parent.parent


parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
args = parser.parse_args()

YEAR = args.year

FEATURE_PATH = (
    ROOT / "data" / "processed" / str(YEAR)
    / f"{YEAR}_feature_stack.tif"
)

REFERENCE_PATH = (
    ROOT / "data" / "reference"
    / "Abuja_LULC_Classification_2024.tif"
)

OUTPUT_DIR = ROOT / "data" / "samples" / f"{YEAR}_specific"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


FEATURES = [
    "B02", "B03", "B04",
    "B08", "B11", "B12",
    "NDVI", "NDBI", "NDWI"
]

CLASS_NAMES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}

SAMPLES_PER_CLASS = 4000
RANDOM_SEED = 42
BLOCK_SIZE = 200


print(f"\nYEAR-SPECIFIC SAMPLE CREATION: {YEAR}")
print("=" * 65)


# ------------------------------------------------------------
# LOAD YEAR FEATURE STACK
# ------------------------------------------------------------

with rasterio.open(FEATURE_PATH) as src:

    features = src.read().astype(np.float32)

    transform = src.transform
    crs = src.crs
    height = src.height
    width = src.width

print(
    f"Feature grid: {width} x {height}"
)

print(
    f"CRS: {crs}"
)


# ------------------------------------------------------------
# ALIGN REFERENCE CLASSIFICATION
# ------------------------------------------------------------

reference = np.full(
    (height, width),
    -1,
    dtype=np.int16,
)

with rasterio.open(REFERENCE_PATH) as src:

    reproject(
        source=rasterio.band(src, 1),
        destination=reference,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=crs,
        resampling=Resampling.nearest,
        dst_nodata=-1,
    )


# ------------------------------------------------------------
# VALID PIXELS
# ------------------------------------------------------------

valid_features = np.all(
    np.isfinite(features),
    axis=0,
)

valid_classes = np.isin(
    reference,
    list(CLASS_NAMES.keys()),
)

valid = valid_features & valid_classes

rows, cols = np.where(valid)

print(
    f"Valid candidate pixels: {len(rows):,}"
)


# ------------------------------------------------------------
# BUILD CANDIDATE TABLE
# ------------------------------------------------------------

data = {
    name: features[i, rows, cols]
    for i, name in enumerate(FEATURES)
}

data["row"] = rows
data["col"] = cols
data["class_code"] = reference[rows, cols]

df = pd.DataFrame(data)

df["class_name"] = df[
    "class_code"
].map(CLASS_NAMES)


# ------------------------------------------------------------
# SPATIAL BLOCKS
# ------------------------------------------------------------

df["block_row"] = (
    df["row"] // BLOCK_SIZE
)

df["block_col"] = (
    df["col"] // BLOCK_SIZE
)

df["block_id"] = (
    df["block_row"].astype(str)
    + "_"
    + df["block_col"].astype(str)
)


# ------------------------------------------------------------
# BALANCED SAMPLING
# ------------------------------------------------------------

rng = np.random.default_rng(
    RANDOM_SEED
)

selected = []

for class_code, class_name in CLASS_NAMES.items():

    class_df = df[
        df["class_code"] == class_code
    ]

    print(
        f"{class_name:12s}: "
        f"{len(class_df):,} candidates"
    )

    if len(class_df) == 0:
        raise RuntimeError(
            f"No samples available for "
            f"{class_name}"
        )

    n = min(
        SAMPLES_PER_CLASS,
        len(class_df),
    )

    chosen = rng.choice(
        class_df.index.to_numpy(),
        size=n,
        replace=False,
    )

    selected.append(
        class_df.loc[chosen]
    )


samples = pd.concat(
    selected,
    ignore_index=True,
)

samples = samples.sample(
    frac=1,
    random_state=RANDOM_SEED,
).reset_index(drop=True)


# ------------------------------------------------------------
# SPATIAL BLOCK SPLIT
# ------------------------------------------------------------

blocks = samples[
    "block_id"
].unique()

rng = np.random.default_rng(
    RANDOM_SEED
)

n_validation = max(
    1,
    int(len(blocks) * 0.20)
)

validation_blocks = set(
    rng.choice(
        blocks,
        size=n_validation,
        replace=False,
    )
)

validation_mask = samples[
    "block_id"
].isin(validation_blocks)

validation = samples[
    validation_mask
].copy()

training = samples[
    ~validation_mask
].copy()


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

all_path = (
    OUTPUT_DIR
    / f"{YEAR}_samples.csv"
)

train_path = (
    OUTPUT_DIR
    / f"{YEAR}_train.csv"
)

valid_path = (
    OUTPUT_DIR
    / f"{YEAR}_validation.csv"
)

samples.to_csv(
    all_path,
    index=False,
)

training.to_csv(
    train_path,
    index=False,
)

validation.to_csv(
    valid_path,
    index=False,
)


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 65)
print(f"{YEAR} SAMPLE SUMMARY")
print("=" * 65)

print(
    f"Total samples:    {len(samples):,}"
)

print(
    f"Training samples: {len(training):,}"
)

print(
    f"Validation:       {len(validation):,}"
)

print("\nTraining classes:")
print(
    training["class_name"]
    .value_counts()
    .sort_index()
)

print("\nValidation classes:")
print(
    validation["class_name"]
    .value_counts()
    .sort_index()
)

print("\nSaved:")
print(all_path)
print(train_path)
print(valid_path)

print(
    "\nNOTE: Labels originate from the existing "
    "2024 classification raster and are therefore "
    "pseudo-labels rather than independent historical "
    "ground truth."
)
