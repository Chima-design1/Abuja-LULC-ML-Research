import argparse
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    cohen_kappa_score,
)


ROOT = Path(__file__).resolve().parent.parent


parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
args = parser.parse_args()

YEAR = args.year

TRAIN_FILE = (
    ROOT / "data" / "samples"
    / f"{YEAR}_specific"
    / f"{YEAR}_train.csv"
)

VALID_FILE = (
    ROOT / "data" / "samples"
    / f"{YEAR}_specific"
    / f"{YEAR}_validation.csv"
)

OUTPUT_DIR = (
    ROOT / "outputs"
    / f"classification_{YEAR}"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


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


print(f"\nYEAR-SPECIFIC RANDOM FOREST: {YEAR}")
print("=" * 70)


# ------------------------------------------------------------
# LOAD
# ------------------------------------------------------------

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALID_FILE)

X_train = train[FEATURES].to_numpy()
y_train = train["class_code"].to_numpy()

X_valid = validation[FEATURES].to_numpy()
y_valid = validation["class_code"].to_numpy()

print(f"Training samples:   {len(y_train):,}")
print(f"Validation samples: {len(y_valid):,}")


# ------------------------------------------------------------
# TRAIN
# ------------------------------------------------------------

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_features="sqrt",
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)

model.fit(
    X_train,
    y_train,
)

print("Training complete.")


# ------------------------------------------------------------
# VALIDATE
# ------------------------------------------------------------

y_pred = model.predict(
    X_valid
)

accuracy = accuracy_score(
    y_valid,
    y_pred,
)

kappa = cohen_kappa_score(
    y_valid,
    y_pred,
)

labels = list(
    CLASS_NAMES.keys()
)

cm = confusion_matrix(
    y_valid,
    y_pred,
    labels=labels,
)

report = classification_report(
    y_valid,
    y_pred,
    labels=labels,
    target_names=list(
        CLASS_NAMES.values()
    ),
    output_dict=True,
    zero_division=0,
)

report_df = pd.DataFrame(
    report
).transpose()


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print(f"{YEAR} SPATIAL VALIDATION RESULTS")
print("=" * 70)

print(
    f"\nOverall Accuracy: {accuracy:.4f}"
)

print(
    f"Cohen's Kappa:    {kappa:.4f}"
)

print("\nConfusion Matrix")

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

print(cm_df)

print("\nClassification Report")

print(
    report_df[
        [
            "precision",
            "recall",
            "f1-score",
            "support",
        ]
    ].round(4)
)


# ------------------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------------------

importance = pd.DataFrame(
    {
        "feature": FEATURES,
        "importance":
            model.feature_importances_,
    }
).sort_values(
    "importance",
    ascending=False,
)

print("\nFeature Importance")

print(
    importance.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# SAVE
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
    OUTPUT_DIR
    / f"accuracy_metrics_{YEAR}.csv",
    index=False,
)

cm_df.to_csv(
    OUTPUT_DIR
    / f"confusion_matrix_{YEAR}.csv"
)

report_df.to_csv(
    OUTPUT_DIR
    / f"classification_report_{YEAR}.csv"
)

importance.to_csv(
    OUTPUT_DIR
    / f"feature_importance_{YEAR}.csv",
    index=False,
)

joblib.dump(
    model,
    OUTPUT_DIR
    / f"random_forest_{YEAR}.joblib",
)

print("\nResults saved to:")
print(OUTPUT_DIR)

print(
    "\nNOTE: Validation is spatially held out "
    "but uses pseudo-labels derived from the "
    "2024 classification raster."
)
