from pathlib import Path
from urllib.parse import urlparse
import os
import boto3
from pystac_client import Client
from botocore.exceptions import ClientError

# ---------------------------------------------------------
# Abuja LULC Sentinel-2 Downloader
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

STAC_URL = "https://stac.dataspace.copernicus.eu/v1"
S3_ENDPOINT = "https://eodata.dataspace.copernicus.eu"

# Required Sentinel-2 assets
REQUIRED_ASSETS = [
    "B02_10m",
    "B03_10m",
    "B04_10m",
    "B08_10m",
    "B11_20m",
    "B12_20m",
    "SCL_20m",
]

# Selected scenes
SCENES = {
    2018: [
        "S2B_MSIL2A_20180128T095239_N0500_R079_T32PLR_20230824T195825",
        "S2B_MSIL2A_20180128T095239_N0500_R079_T32PLQ_20230824T195825",
    ],
    2020: [
        "S2A_MSIL2A_20200113T095351_N0500_R079_T32PLR_20230428T210929",
        "S2A_MSIL2A_20200113T095351_N0500_R079_T32PLQ_20230428T210929",
    ],
    2022: [
        "S2A_MSIL2A_20220122T095321_N0510_R079_T32PLR_20240504T045544",
        "S2A_MSIL2A_20220122T095321_N0510_R079_T32PLQ_20240504T045544",
    ],
    2024: [
        "S2A_MSIL2A_20240122T095311_N0510_R079_T32PLR_20240122T132047",
        "S2A_MSIL2A_20240122T095311_N0510_R079_T32PLQ_20240122T132047",
    ],
}

# ---------------------------------------------------------
# Check credentials
# ---------------------------------------------------------

access_key = os.environ.get("CDSE_S3_ACCESS_KEY")
secret_key = os.environ.get("CDSE_S3_SECRET_KEY")

if not access_key or not secret_key:
    raise RuntimeError(
        "CDSE S3 credentials are missing from this PowerShell session."
    )

# ---------------------------------------------------------
# Connect to CDSE STAC
# ---------------------------------------------------------

print("=" * 70)
print("ABUJA LULC - SENTINEL-2 DATA DOWNLOADER")
print("=" * 70)
print()

catalog = Client.open(STAC_URL)

# ---------------------------------------------------------
# Connect to CDSE S3
# ---------------------------------------------------------

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="default",
)

print("S3 connection: OK")
print()

# ---------------------------------------------------------
# Download function
# ---------------------------------------------------------

def download_asset(year, scene_id, asset_name, href):
    parsed = urlparse(href)

    if parsed.scheme != "s3":
        raise RuntimeError(
            f"Unexpected asset URL for {scene_id} / {asset_name}: {href}"
        )

    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    # Preserve the original filename
    filename = Path(key).name

    year_dir = RAW_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    output_file = year_dir / filename

    if output_file.exists():
        print(f"  SKIP: {filename} already exists")
        return

    print(f"  Downloading: {filename}")

    try:
        s3.download_file(
            bucket,
            key,
            str(output_file),
        )

        size_mb = output_file.stat().st_size / (1024 * 1024)

        print(f"  DONE: {filename} ({size_mb:.1f} MB)")

    except Exception:
        if output_file.exists():
            output_file.unlink()
        raise


# ---------------------------------------------------------
# Process scenes
# ---------------------------------------------------------

total_downloaded = 0
total_skipped = 0

for year, scene_ids in SCENES.items():

    print()
    print("=" * 70)
    print(f"YEAR: {year}")
    print("=" * 70)

    for scene_id in scene_ids:

        print()
        print(f"Scene: {scene_id}")

        try:
            search = catalog.search(
                collections=["sentinel-2-l2a"],
                ids=[scene_id],
            )

            items = list(search.items())

            if not items:
                print("  ERROR: Scene not found in STAC catalog.")
                continue

            item = items[0]

            print(f"  Date: {item.datetime}")
            print(f"  Cloud cover: {item.properties.get('eo:cloud_cover')}%")

            for asset_name in REQUIRED_ASSETS:

                if asset_name not in item.assets:
                    print(f"  ERROR: Missing asset {asset_name}")
                    continue

                href = item.assets[asset_name].href

                try:
                    output_before = list((RAW_DIR / str(year)).glob("*"))

                    download_asset(
                        year,
                        scene_id,
                        asset_name,
                        href,
                    )

                    output_after = list((RAW_DIR / str(year)).glob("*"))

                    if len(output_after) > len(output_before):
                        total_downloaded += 1
                    else:
                        total_skipped += 1

                except Exception as e:
                    print(f"  ERROR downloading {asset_name}: {e}")

        except Exception as e:
            print(f"  ERROR processing scene: {e}")


# ---------------------------------------------------------
# Final summary
# ---------------------------------------------------------

print()
print("=" * 70)
print("DOWNLOAD PROCESS FINISHED")
print("=" * 70)

print(f"New files downloaded: {total_downloaded}")
print(f"Existing files skipped: {total_skipped}")

print()
print("Data directory:")
print(RAW_DIR)

print()
print("Downloaded files by year:")

for year in SCENES:
    year_dir = RAW_DIR / str(year)

    if year_dir.exists():
        files = list(year_dir.iterdir())

        print()
        print(f"{year}: {len(files)} files")

        for file in files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  {file.name}  ({size_mb:.1f} MB)")

print()
print("NEXT STEP: Sentinel-2 preprocessing and cloud masking.")
