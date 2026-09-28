import rasterio
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

YEARS = [2018, 2020, 2022, 2024]

EXPECTED_BANDS = [
    "B02", "B03", "B04", "B08",
    "B11", "B12", "NDVI", "NDBI", "NDWI"
]

print("=" * 70)
print("ABUJA LULC FEATURE STACK QUALITY CONTROL")
print("=" * 70)

datasets = {}

for year in YEARS:
    path = PROCESSED_DIR / str(year) / f"{year}_feature_stack.tif"

    print(f"\n{'=' * 70}")
    print(f"CHECKING {year}")
    print("=" * 70)

    if not path.exists():
        print("ERROR: Feature stack not found:")
        print(path)
        continue

    with rasterio.open(path) as src:

        datasets[year] = {
            "crs": src.crs,
            "width": src.width,
            "height": src.height,
            "transform": src.transform,
            "res": src.res,
            "bounds": src.bounds,
        }

        print(f"File: {path}")
        print(f"CRS: {src.crs}")
        print(f"Dimensions: {src.width} x {src.height}")
        print(f"Resolution: {src.res}")
        print(f"Bands: {src.count}")
        print(f"NoData: {src.nodata}")

        print("\nBand names:")
        for i, name in enumerate(src.descriptions, start=1):
            print(f"  {i}: {name}")

        print("\nStructural checks:")

        if src.count == 9:
            print("  Band count: PASS")
        else:
            print(f"  Band count: FAIL - expected 9, found {src.count}")

        if list(src.descriptions) == EXPECTED_BANDS:
            print("  Band order: PASS")
        else:
            print("  Band order: REVIEW")

        if src.crs.to_epsg() == 32632:
            print("  CRS EPSG:32632: PASS")
        else:
            print(f"  CRS: REVIEW - {src.crs}")

        if all(abs(r - 10.0) < 0.01 for r in src.res):
            print("  10 m resolution: PASS")
        else:
            print(f"  Resolution: REVIEW - {src.res}")

        print("\nData statistics:")

        for band_number, band_name in enumerate(src.descriptions, start=1):

            data = src.read(band_number, masked=True)
            values = data.compressed()

            if values.size == 0:
                print(f"  {band_name}: NO VALID PIXELS")
                continue

            values = values[np.isfinite(values)]

            if values.size == 0:
                print(f"  {band_name}: NO FINITE VALUES")
                continue

            print(
                f"  {band_name}: "
                f"min={values.min():.4f}, "
                f"max={values.max():.4f}, "
                f"mean={values.mean():.4f}, "
                f"valid={values.size:,}"
            )


print("\n")
print("=" * 70)
print("CROSS-YEAR SPATIAL CONSISTENCY")
print("=" * 70)

if len(datasets) == len(YEARS):

    reference_year = YEARS[0]
    reference = datasets[reference_year]

    print(f"\nReference year: {reference_year}")

    overall_pass = True

    for year in YEARS[1:]:

        current = datasets[year]

        print(f"\n{year} vs {reference_year}:")

        checks = {
            "CRS": current["crs"] == reference["crs"],
            "Dimensions": (
                current["width"] == reference["width"]
                and current["height"] == reference["height"]
            ),
            "Resolution": current["res"] == reference["res"],
            "Transform": current["transform"] == reference["transform"],
            "Bounds": current["bounds"] == reference["bounds"],
        }

        for name, passed in checks.items():

            status = "PASS" if passed else "FAIL"

            print(f"  {name}: {status}")

            if not passed:
                overall_pass = False

    print("\n" + "=" * 70)

    if overall_pass:
        print("OVERALL QC RESULT: PASS")
        print("All four feature stacks are spatially consistent.")
    else:
        print("OVERALL QC RESULT: REVIEW REQUIRED")
        print("One or more spatial checks failed.")

else:

    print("ERROR: Not all four feature stacks were found.")
    print("QC cannot be completed.")

print("=" * 70)
