from pathlib import Path

import joblib
import numpy as np
import rasterio


ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs" / "lulc_maps"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

YEARS = [2018, 2020, 2022, 2024]

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


MODEL_PATHS = {
    2018: ROOT / "outputs" / "classification_2018" / "random_forest_2018.joblib",
    2020: ROOT / "outputs" / "classification_2020" / "random_forest_2020.joblib",
    2022: ROOT / "outputs" / "classification_2022" / "random_forest_2022.joblib",
    2024: ROOT / "outputs" / "classification_spatial" / "random_forest_spatial_2024.joblib",
}


print("\nYEAR-SPECIFIC MULTI-YEAR CLASSIFICATION")
print("=" * 60)


for year in YEARS:

    print("\n" + "=" * 60)
    print(f"CLASSIFYING {year}")
    print("=" * 60)

    model_path = MODEL_PATHS[year]

    print(f"Model: {model_path}")

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found for {year}: {model_path}"
        )

    model = joblib.load(model_path)

    print("Model loaded successfully.")

    feature_path = (
        PROCESSED_DIR
        / str(year)
        / f"{year}_feature_stack.tif"
    )

    if not feature_path.exists():
        raise FileNotFoundError(
            f"Feature stack not found for {year}: {feature_path}"
        )

    output_path = (
        OUTPUT_DIR
        / f"Abuja_LULC_{year}_year_specific.tif"
    )

    with rasterio.open(feature_path) as src:

        profile = src.profile.copy()

        height = src.height
        width = src.width

        print(
            f"Input grid: {width} x {height}"
        )

        print(
            f"CRS: {src.crs}"
        )

        data = src.read().astype(
            np.float32
        )

        X = data.reshape(
            data.shape[0],
            -1,
        ).T

        valid = np.all(
            np.isfinite(X),
            axis=1,
        )

        print(
            f"Valid pixels: "
            f"{valid.sum():,}"
        )

        print(
            f"Masked pixels: "
            f"{(~valid).sum():,}"
        )

        prediction = np.full(
            X.shape[0],
            255,
            dtype=np.uint8,
        )

        prediction[valid] = model.predict(
            X[valid]
        ).astype(np.uint8)

        prediction = prediction.reshape(
            height,
            width,
        )

        profile.update(
            count=1,
            dtype="uint8",
            nodata=255,
            compress="lzw",
        )

        with rasterio.open(
            output_path,
            "w",
            **profile,
        ) as dst:

            dst.write(
                prediction,
                1,
            )

            dst.set_band_description(
                1,
                "LULC class",
            )

    print(
        f"Saved: {output_path}"
    )

    classes, counts = np.unique(
        prediction[prediction != 255],
        return_counts=True,
    )

    total_valid = counts.sum()

    print("\nClass pixel counts:")

    for cls, count in zip(
        classes,
        counts,
    ):

        percentage = (
            count / total_valid * 100
        )

        print(
            f"  Class {cls}: "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )


print("\n" + "=" * 60)
print("YEAR-SPECIFIC CLASSIFICATION COMPLETE")
print("=" * 60)

print(f"Outputs: {OUTPUT_DIR}")
