from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    cohen_kappa_score,
)
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "samples" / "training_samples_2024_clean.csv"

OUTPUT_DIR = ROOT / "outputs" / "classification"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
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

CLASS_NAMES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading training samples...")

df = pd.read_csv(INPUT)

X = df[FEATURES].to_numpy(dtype=np.float32)
y = df["class_code"].to_numpy(dtype=np.int16)


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print(f"Total samples:      {len(y):,}")
print(f"Training samples:   {len(y_train):,}")
print(f"Validation samples: {len(y_val):,}")


# ============================================================
# RANDOM FOREST
# ============================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_features="sqrt",
    min_samples_leaf=2,
    class_weight=None,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

print("Training complete.")


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(X_val)


# ============================================================
# ACCURACY
# ============================================================

accuracy = accuracy_score(y_val, y_pred)

kappa = cohen_kappa_score(
    y_val,
    y_pred,
)

print("\n" + "=" * 70)
print("RANDOM FOREST VALIDATION")
print("=" * 70)

print(f"\nOverall Accuracy: {accuracy:.4f}")
print(f"Cohen's Kappa:    {kappa:.4f}")


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_val,
    y_pred,
    labels=list(CLASS_NAMES.keys()),
)

print("\nConfusion Matrix")
print("----------------")

print(
    pd.DataFrame(
        cm,
        index=[
            f"Actual {CLASS_NAMES[i]}"
            for i in CLASS_NAMES
        ],
        columns=[
            f"Pred {CLASS_NAMES[i]}"
            for i in CLASS_NAMES
        ],
    )
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

report = classification_report(
    y_val,
    y_pred,
    labels=list(CLASS_NAMES.keys()),
    target_names=list(CLASS_NAMES.values()),
    output_dict=True,
    zero_division=0,
)

report_df = pd.DataFrame(report).transpose()

print("\nClassification Report")
print("---------------------")

print(
    report_df[
        ["precision", "recall", "f1-score", "support"]
    ].round(4)
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame(
    {
        "feature": FEATURES,
        "importance": model.feature_importances_,
    }
).sort_values(
    "importance",
    ascending=False,
)

print("\nFeature Importance")
print("------------------")

print(
    importance.to_string(
        index=False,
        formatters={
            "importance": "{:.4f}".format
        },
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

pd.DataFrame(
    cm,
    index=list(CLASS_NAMES.values()),
    columns=list(CLASS_NAMES.values()),
).to_csv(
    OUTPUT_DIR / "confusion_matrix_2024.csv"
)

report_df.to_csv(
    OUTPUT_DIR / "classification_report_2024.csv"
)

importance.to_csv(
    OUTPUT_DIR / "feature_importance_2024.csv",
    index=False,
)

metrics = pd.DataFrame(
    {
        "metric": [
            "overall_accuracy",
            "cohen_kappa",
        ],
        "value": [
            accuracy,
            kappa,
        ],
    }
)

metrics.to_csv(
    OUTPUT_DIR / "accuracy_metrics_2024.csv",
    index=False,
)


# ============================================================
# SAVE MODEL
# ============================================================

import joblib

joblib.dump(
    model,
    OUTPUT_DIR / "random_forest_2024.joblib",
)


print("\nResults saved to:")
print(OUTPUT_DIR)

print(
    "\nNOTE: Validation uses pseudo-labels derived from "
    "the existing 2024 classification raster. "
    "It is therefore not independent ground-truth validation."
)