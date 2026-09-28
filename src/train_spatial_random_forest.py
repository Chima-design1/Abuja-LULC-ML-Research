from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    cohen_kappa_score,
)


ROOT = Path(__file__).resolve().parent.parent

TRAIN_FILE = ROOT / "data" / "samples" / "spatial_train_2024.csv"
VALID_FILE = ROOT / "data" / "samples" / "spatial_validation_2024.csv"

OUTPUT_DIR = ROOT / "outputs" / "classification_spatial"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


print("\nSPATIAL RANDOM FOREST VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALID_FILE)

X_train = train[FEATURES].to_numpy(dtype=np.float32)
y_train = train["class_code"].to_numpy(dtype=np.int16)

X_valid = validation[FEATURES].to_numpy(dtype=np.float32)
y_valid = validation["class_code"].to_numpy(dtype=np.int16)

print(f"Training samples:   {len(y_train):,}")
print(f"Validation samples: {len(y_valid):,}")


# ------------------------------------------------------------
# TRAIN RANDOM FOREST
# ------------------------------------------------------------

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_features="sqrt",
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

print("Training complete.")


# ------------------------------------------------------------
# PREDICT
# ------------------------------------------------------------

y_pred = model.predict(X_valid)


# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

accuracy = accuracy_score(
    y_valid,
    y_pred,
)

kappa = cohen_kappa_score(
    y_valid,
    y_pred,
)

print("\n" + "=" * 70)
print("SPATIAL VALIDATION RESULTS")
print("=" * 70)

print(f"\nOverall Accuracy: {accuracy:.4f}")
print(f"Cohen's Kappa:    {kappa:.4f}")


# ------------------------------------------------------------
# CONFUSION MATRIX
# ------------------------------------------------------------

labels = list(CLASS_NAMES.keys())

cm = confusion_matrix(
    y_valid,
    y_pred,
    labels=labels,
)

cm_df = pd.DataFrame(
    cm,
    index=[
        f"Actual {CLASS_NAMES[i]}"
        for i in labels
    ],
    columns=[
        f"Pred {CLASS_NAMES[i]}"
        for i in labels
    ],
)

print("\nConfusion Matrix")
print(cm_df)


# ------------------------------------------------------------
# CLASSIFICATION REPORT
# ------------------------------------------------------------

report = classification_report(
    y_valid,
    y_pred,
    labels=labels,
    target_names=list(CLASS_NAMES.values()),
    output_dict=True,
    zero_division=0,
)

report_df = pd.DataFrame(report).transpose()

print("\nClassification Report")
print(
    report_df[
        ["precision", "recall", "f1-score", "support"]
    ].round(4)
)


# ------------------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------------------

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
print(importance.to_string(index=False))


# ------------------------------------------------------------
# SAVE RESULTS
# ------------------------------------------------------------

pd.DataFrame(
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
).to_csv(
    OUTPUT_DIR / "spatial_accuracy_metrics_2024.csv",
    index=False,
)

cm_df.to_csv(
    OUTPUT_DIR / "spatial_confusion_matrix_2024.csv"
)

report_df.to_csv(
    OUTPUT_DIR / "spatial_classification_report_2024.csv"
)

importance.to_csv(
    OUTPUT_DIR / "spatial_feature_importance_2024.csv",
    index=False,
)

joblib.dump(
    model,
    OUTPUT_DIR / "random_forest_spatial_2024.joblib",
)


print("\nResults saved to:")
print(OUTPUT_DIR)

print(
    "\nNOTE: The validation samples are spatially held out, "
    "but their labels originate from the existing 2024 "
    "classification raster. Therefore this remains "
    "pseudo-label validation rather than independent "
    "field/reference validation."
)