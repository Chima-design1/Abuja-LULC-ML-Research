from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling
from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

FEATURE_PATH = ROOT / "data" / "processed" / "2024" / "2024_feature_stack.tif"
REFERENCE_PATH = ROOT / "data" / "reference" / "Abuja_LULC_Classification_2024.tif"

OUTPUT_DIR = ROOT / "data" / "samples"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUTPUT_DIR / "training_samples_2024.csv"


# ============================================================
# SETTINGS
# ============================================================

CLASS_NAMES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}

FEATURE_NAMES = [
    "B02",
    "B03",
    "B04",
    "B08",
    "B11",
    "B12",
    "NDVI",
    "NDBI",
    "NDWI",
]

SAMPLES_PER_CLASS = 5000

RANDOM_SEED = 42

# Validation fraction is kept spatially separate later in the
# modelling stage. This split is only for reproducible sampling.
VALIDATION_FRACTION = 0.20


# ============================================================
# LOAD FEATURE STACK
# ============================================================

print("\nLoading 2024 feature stack...")

with rasterio.open(FEATURE_PATH) as src:
    features = src.read().astype(np.float32)
    feature_profile = src.profile.copy()
    feature_transform = src.transform
    feature_crs = src.crs
    feature_height = src.height
    feature_width = src.width

print(f"Feature stack: {feature_width} x {feature_height}")
print(f"Bands: {features.shape[0]}")
print(f"CRS: {feature_crs}")


# ============================================================
# LOAD AND REPROJECT REFERENCE CLASSIFICATION
# ============================================================

print("\nLoading reference classification...")

reference = np.full(
    (feature_height, feature_width),
    -1,
    dtype=np.int16,
)

with rasterio.open(REFERENCE_PATH) as src:

    reproject(
        source=rasterio.band(src, 1),
        destination=reference,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=feature_transform,
        dst_crs=feature_crs,
        resampling=Resampling.nearest,
        dst_nodata=-1,
    )

print("Reference raster aligned to feature-stack grid.")


# ============================================================
# VALID PIXELS
# ============================================================

print("\nFinding valid pixels...")

# All nine predictors must be finite.
valid_features = np.all(np.isfinite(features), axis=0)

# Only the five expected classes are accepted.
valid_classes = np.isin(
    reference,
    list(CLASS_NAMES.keys()),
)

valid_mask = valid_features & valid_classes

rows, cols = np.where(valid_mask)

print(f"Valid candidate pixels: {len(rows):,}")


# ============================================================
# CONVERT FEATURES TO TABLE
# ============================================================

print("\nPreparing candidate sample table...")

candidate_data = {
    name: features[i, rows, cols]
    for i, name in enumerate(FEATURE_NAMES)
}

candidate_data["row"] = rows
candidate_data["col"] = cols
candidate_data["class_code"] = reference[rows, cols]

samples = pd.DataFrame(candidate_data)

samples["class_name"] = samples["class_code"].map(CLASS_NAMES)

print("\nCandidate class distribution:")

print(
    samples["class_name"]
    .value_counts()
    .sort_index()
)


# ============================================================
# BALANCED SAMPLING
# ============================================================

print("\nSelecting balanced samples...")

rng = np.random.default_rng(RANDOM_SEED)

selected = []

for class_code, class_name in CLASS_NAMES.items():

    class_samples = samples[
        samples["class_code"] == class_code
    ]

    available = len(class_samples)

    if available == 0:
        raise RuntimeError(
            f"No candidate pixels available for class "
            f"{class_code} ({class_name})."
        )

    n = min(
        SAMPLES_PER_CLASS,
        available,
    )

    indices = rng.choice(
        class_samples.index.to_numpy(),
        size=n,
        replace=False,
    )

    selected.append(
        class_samples.loc[indices]
    )

    print(
        f"{class_code} - {class_name}: "
        f"{n:,} samples selected "
        f"(available: {available:,})"
    )


training_samples = pd.concat(
    selected,
    ignore_index=True,
)

# Shuffle
training_samples = training_samples.sample(
    frac=1,
    random_state=RANDOM_SEED,
).reset_index(drop=True)


# ============================================================
# REPRODUCIBLE TRAIN/VALIDATION SPLIT
# ============================================================

train_df, validation_df = train_test_split(
    training_samples,
    test_size=VALIDATION_FRACTION,
    random_state=RANDOM_SEED,
    stratify=training_samples["class_code"],
)

train_df = train_df.reset_index(drop=True)
validation_df = validation_df.reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

training_samples.to_csv(
    OUTPUT_CSV,
    index=False,
)

train_df.to_csv(
    OUTPUT_DIR / "training_samples_2024_train.csv",
    index=False,
)

validation_df.to_csv(
    OUTPUT_DIR / "training_samples_2024_validation.csv",
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("TRAINING SAMPLE CREATION COMPLETE")
print("=" * 60)

print(f"Total samples:      {len(training_samples):,}")
print(f"Training samples:   {len(train_df):,}")
print(f"Validation samples: {len(validation_df):,}")

print("\nTraining distribution:")
print(
    train_df["class_name"]
    .value_counts()
    .sort_index()
)

print("\nValidation distribution:")
print(
    validation_df["class_name"]
    .value_counts()
    .sort_index()
)

print("\nSaved:")
print(OUTPUT_CSV)
print(OUTPUT_DIR / "training_samples_2024_train.csv")
print(OUTPUT_DIR / "training_samples_2024_validation.csv")

print(
    "\nNOTE: These labels originate from the existing 2024 "
    "classification raster and therefore are pseudo-labels, "
    "not independent ground truth."
)