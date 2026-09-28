from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio.warp import reproject
from rasterio.transform import from_bounds

# ============================================================
# Abuja LULC - Sentinel-2 Preprocessing
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
STUDY_AREA = RAW_DIR / "abuja_study_area.geojson"

YEARS = [2018, 2020, 2022, 2024]

# Sentinel-2 bands required
BANDS_10M = ["B02", "B03", "B04", "B08"]
BANDS_20M = ["B11", "B12", "SCL"]

# SCL classes to KEEP
# 4 = Vegetation
# 5 = Not-vegetated
# 6 = Water
# 7 = Unclassified
# 11 = Snow/Ice
#
# Cloud/shadow classes removed:
# 0, 1, 2, 3, 8, 9, 10
VALID_SCL = [4, 5, 6, 7, 11]

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def find_band_files(year, band):
    files = sorted(
        (RAW_DIR / str(year)).glob(f"*_{band}_*.jp2")
    )

    if not files:
        raise FileNotFoundError(
            f"No files found for {year} {band}"
        )

    return files

def mosaic_band(files):
    datasets = [rasterio.open(f) for f in files]

    try:
        mosaic, transform = merge(datasets)

        profile = datasets[0].profile.copy()

        profile.update(
            height=mosaic.shape[1],
            width=mosaic.shape[2],
            transform=transform,
            count=1,
        )

        return mosaic[0], transform, profile

    finally:
        for ds in datasets:
            ds.close()


def clip_array(array, transform, profile, geometry):
    temp_profile = profile.copy()

    temp_profile.update(
        height=array.shape[0],
        width=array.shape[1],
        transform=transform,
        count=1,
    )

    temp_path = PROCESSED_DIR / "_temporary_input.tif"

    with rasterio.open(
        temp_path,
        "w",
        **temp_profile
    ) as dst:
        dst.write(array, 1)

    with rasterio.open(temp_path) as src:
        clipped, clipped_transform = mask(
            src,
            geometry,
            crop=True,
            nodata=0,
        )
        clipped_profile = src.profile.copy()

    temp_path.unlink(missing_ok=True)

    clipped_profile.update(
        height=clipped.shape[1],
        width=clipped.shape[2],
        transform=clipped_transform,
        count=1,
    )

    return clipped[0], clipped_transform, clipped_profile


def resample_to_grid(
    source_array,
    source_transform,
    source_crs,
    target_shape,
    target_transform,
    target_crs,
    source_dtype,
    resampling_method,
):
    destination = np.zeros(
        target_shape,
        dtype=source_dtype
    )

    reproject(
        source=source_array,
        destination=destination,
        src_transform=source_transform,
        src_crs=source_crs,
        dst_transform=target_transform,
        dst_crs=target_crs,
        src_nodata=0,
        dst_nodata=0,
        resampling=resampling_method,
    )

    return destination


def save_raster(path, array, profile, dtype=None, nodata=0):

    profile = profile.copy()

    if dtype is None:
        dtype = str(array.dtype)

    profile.update(
        driver="GTiff",
        dtype=dtype,
        count=1,
        compress="deflate",
        predictor=2,
        nodata=nodata,
    )

    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype(dtype), 1)


# ============================================================
# Process each year
# ============================================================

study_area = gpd.read_file(STUDY_AREA)

for year in YEARS:

    print()
    print("=" * 70)
    print(f"PROCESSING {year}")
    print("=" * 70)

    year_dir = PROCESSED_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Reproject study area to Sentinel-2 UTM CRS
    # --------------------------------------------------------

    first_band = find_band_files(year, "B02")[0]

    with rasterio.open(first_band) as src:
        target_crs = src.crs
        target_res = src.res

    study_projected = study_area.to_crs(target_crs)

    geometry = study_projected.geometry.values

    print("Target CRS:", target_crs)
    print("Target resolution:", target_res)

    # --------------------------------------------------------
    # Process 10 m bands
    # --------------------------------------------------------

    bands = {}

    for band in BANDS_10M:

        print(f"Processing {band}...")

        files = find_band_files(year, band)

        array, transform, profile = mosaic_band(files)

        clipped, clipped_transform, clipped_profile = clip_array(
            array,
            transform,
            profile,
            geometry,
        )

        bands[band] = clipped.astype(np.float32)

        save_raster(
            year_dir / f"{year}_{band}_10m_clipped.tif",
            clipped,
            clipped_profile,
            dtype="float32",
        )

    # --------------------------------------------------------
    # Establish common analysis grid
    # --------------------------------------------------------

    reference = bands["B02"]

    with rasterio.open(
        year_dir / f"{year}_B02_10m_clipped.tif"
    ) as src:
        target_transform = src.transform
        target_profile = src.profile.copy()
        target_crs = src.crs
        target_height = src.height
        target_width = src.width

    target_shape = (
        target_height,
        target_width,
    )

    # --------------------------------------------------------
    # Process 20 m bands and resample to 10 m
    # --------------------------------------------------------

    for band in ["B11", "B12"]:

        print(f"Processing {band} (20m -> 10m)...")

        files = find_band_files(year, band)

        array, transform, profile = mosaic_band(files)

        clipped, clipped_transform, clipped_profile = clip_array(
            array,
            transform,
            profile,
            geometry,
        )

        resampled = resample_to_grid(
            clipped,
            clipped_transform,
            target_crs,
            target_shape,
            target_transform,
            target_crs,
            np.float32,
            Resampling.bilinear,
        )

        bands[band] = resampled

        save_raster(
            year_dir / f"{year}_{band}_10m_resampled.tif",
            resampled,
            target_profile,
            dtype="float32",
        )

    # --------------------------------------------------------
    # Process SCL
    # --------------------------------------------------------

    print("Processing SCL (20m -> 10m)...")

    files = find_band_files(year, "SCL")

    array, transform, profile = mosaic_band(files)

    clipped, clipped_transform, clipped_profile = clip_array(
        array,
        transform,
        profile,
        geometry,
    )

    scl = resample_to_grid(
        clipped,
        clipped_transform,
        target_crs,
        target_shape,
        target_transform,
        target_crs,
        np.uint8,
        Resampling.nearest,
    )

    save_raster(
        year_dir / f"{year}_SCL_10m.tif",
        scl,
        target_profile,
        dtype="uint8",
    )

    # --------------------------------------------------------
    # Cloud/shadow mask
    # --------------------------------------------------------

    print("Applying SCL cloud/shadow mask...")

    valid_mask = np.isin(
        scl,
        VALID_SCL,
    )

    # --------------------------------------------------------
    # Sentinel-2 reflectance scaling
    # --------------------------------------------------------

    for band in bands:
        bands[band] = bands[band] / 10000.0

    # --------------------------------------------------------
    # Calculate indices
    # --------------------------------------------------------

    print("Calculating NDVI...")

    ndvi_denominator = (
        bands["B08"] + bands["B04"]
    )

    ndvi = np.divide(
        bands["B08"] - bands["B04"],
        ndvi_denominator,
        out=np.zeros_like(bands["B08"]),
        where=ndvi_denominator != 0,
    )

    print("Calculating NDBI...")

    ndbi_denominator = (
        bands["B11"] + bands["B08"]
    )

    ndbi = np.divide(
        bands["B11"] - bands["B08"],
        ndbi_denominator,
        out=np.zeros_like(bands["B11"]),
        where=ndbi_denominator != 0,
    )

    print("Calculating NDWI...")

    ndwi_denominator = (
        bands["B03"] + bands["B08"]
    )

    ndwi = np.divide(
        bands["B03"] - bands["B08"],
        ndwi_denominator,
        out=np.zeros_like(bands["B03"]),
        where=ndwi_denominator != 0,
    )

    # --------------------------------------------------------
    # Apply mask
    # --------------------------------------------------------

    for name, array in {
        "NDVI": ndvi,
        "NDBI": ndbi,
        "NDWI": ndwi,
    }.items():

        masked = np.where(
            valid_mask,
            array,
            np.nan,
        ).astype(np.float32)

        save_raster(
            year_dir / f"{year}_{name}.tif",
            masked,
            target_profile,
            dtype="float32",
            nodata=np.nan,
        )

    # --------------------------------------------------------
    # Create feature stack
    # --------------------------------------------------------

    print("Creating feature stack...")

    feature_arrays = [
        bands["B02"],
        bands["B03"],
        bands["B04"],
        bands["B08"],
        bands["B11"],
        bands["B12"],
        ndvi,
        ndbi,
        ndwi,
    ]

    feature_names = [
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

    stack = np.stack(feature_arrays)

    for i in range(stack.shape[0]):
        stack[i] = np.where(
            valid_mask,
            stack[i],
            np.nan,
        )

    stack_profile = target_profile.copy()

    stack_profile.update(
        count=len(feature_names),
        dtype="float32",
        nodata=np.nan,
        compress="deflate",
        predictor=2,
    )

    stack_path = year_dir / f"{year}_feature_stack.tif"

    with rasterio.open(
        stack_path,
        "w",
        **stack_profile
    ) as dst:

        for i, name in enumerate(feature_names, start=1):

            dst.write(
                stack[i - 1].astype(np.float32),
                i,
            )

            dst.set_band_description(
                i,
                name,
            )

    print("Feature stack:", stack_path)
    print("Bands:", ", ".join(feature_names))

    print(f"{year} COMPLETE")


print()
print("=" * 70)
print("ALL PREPROCESSING COMPLETE")
print("=" * 70)
