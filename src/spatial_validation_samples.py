from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "samples" / "training_samples_2024_clean.csv"

OUTPUT_DIR = ROOT / "data" / "samples"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_OUTPUT = OUTPUT_DIR / "spatial_train_2024.csv"
VALID_OUTPUT = OUTPUT_DIR / "spatial_validation_2024.csv"


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

RANDOM_SEED = 42

# Approximate spatial block size in pixels.
# The feature stack resolution is 10 m.
BLOCK_SIZE = 200

# Keep approximately 20% of blocks for validation.
VALIDATION_BLOCK_FRACTION = 0.20


# ------------------------------------------------------------
# LOAD SAMPLES
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

print("\nSPATIAL VALIDATION SAMPLE CREATION")
print("=" * 60)

print(f"Input samples: {len(df):,}")


# ------------------------------------------------------------
# CREATE SPATIAL BLOCK IDS
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
# SELECT VALIDATION BLOCKS
# ------------------------------------------------------------

blocks = df["block_id"].unique()

rng = np.random.default_rng(RANDOM_SEED)

n_validation_blocks = max(
    1,
    int(len(blocks) * VALIDATION_BLOCK_FRACTION)
)

validation_blocks = set(
    rng.choice(
        blocks,
        size=n_validation_blocks,
        replace=False,
    )
)


# ------------------------------------------------------------
# SPLIT BY BLOCK
# ------------------------------------------------------------

validation_mask = df["block_id"].isin(
    validation_blocks
)

validation = df.loc[
    validation_mask
].copy()

training = df.loc[
    ~validation_mask
].copy()


# ------------------------------------------------------------
# CHECK CLASS REPRESENTATION
# ------------------------------------------------------------

print(
    f"Total spatial blocks: {len(blocks):,}"
)

print(
    f"Validation blocks:    {len(validation_blocks):,}"
)

print(
    f"Training samples:     {len(training):,}"
)

print(
    f"Validation samples:   {len(validation):,}"
)

print("\nTraining class distribution:")
print(
    training["class_name"]
    .value_counts()
    .sort_index()
)

print("\nValidation class distribution:")
print(
    validation["class_name"]
    .value_counts()
    .sort_index()
)


# ------------------------------------------------------------
# CHECK FOR CLASS ABSENCE
# ------------------------------------------------------------

all_classes = set(
    df["class_code"].unique()
)

train_classes = set(
    training["class_code"].unique()
)

validation_classes = set(
    validation["class_code"].unique()
)

missing_train = (
    all_classes - train_classes
)

missing_validation = (
    all_classes - validation_classes
)

if missing_train:
    print(
        "\nWARNING: Classes missing from training:",
        missing_train
    )

if missing_validation:
    print(
        "\nWARNING: Classes missing from validation:",
        missing_validation
    )


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

training.to_csv(
    TRAIN_OUTPUT,
    index=False,
)

validation.to_csv(
    VALID_OUTPUT,
    index=False,
)


print("\nSaved:")
print(TRAIN_OUTPUT)
print(VALID_OUTPUT)