from pathlib import Path
from urllib.parse import urlparse
import os
import time
import boto3
from pystac_client import Client

RAW_DIR = Path("data/raw")
STAC_URL = "https://stac.dataspace.copernicus.eu/v1"
S3_ENDPOINT = "https://eodata.dataspace.copernicus.eu"

REQUIRED = [
    "B02_10m",
    "B03_10m",
    "B04_10m",
    "B08_10m",
    "B11_20m",
    "B12_20m",
    "SCL_20m",
]

SCENES = {
    2020: "S2A_MSIL2A_20200113T095351_N0500_R079_T32PLQ_20230428T210929",
    2024: "S2A_MSIL2A_20240122T095311_N0510_R079_T32PLQ_20240122T132047",
}

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=os.environ["CDSE_S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["CDSE_S3_SECRET_KEY"],
    region_name="default",
)

def get_item_with_retry(scene_id):
    for attempt in range(1, 6):
        try:
            print(f"  STAC lookup attempt {attempt}/5...")
            catalog = Client.open(STAC_URL)
            items = list(
                catalog.search(
                    collections=["sentinel-2-l2a"],
                    ids=[scene_id],
                ).items()
            )

            if items:
                return items[0]

            print("  Scene not found.")

        except Exception as e:
            print(f"  STAC lookup failed: {type(e).__name__}: {e}")

        if attempt < 5:
            time.sleep(attempt * 10)

    return None


def download_with_retry(bucket, key, output):
    if output.exists():
        print(f"  SKIP: {output.name}")
        return True

    for attempt in range(1, 6):
        try:
            print(
                f"  Downloading {output.name} "
                f"(attempt {attempt}/5)"
            )

            s3.download_file(bucket, key, str(output))

            size = output.stat().st_size / (1024 * 1024)

            print(f"  DONE: {output.name} ({size:.1f} MB)")
            return True

        except Exception as e:
            print(
                f"  Download failed: "
                f"{type(e).__name__}: {e}"
            )

            if output.exists():
                output.unlink()

            if attempt < 5:
                time.sleep(attempt * 10)

    return False


print("=" * 70)
print("RETRYING MISSING T32PLQ DATA")
print("=" * 70)

for year, scene_id in SCENES.items():

    print()
    print("=" * 70)
    print(f"YEAR: {year}")
    print("=" * 70)

    item = get_item_with_retry(scene_id)

    if item is None:
        print("FAILED: Could not retrieve STAC item.")
        continue

    print(f"Date: {item.datetime}")
    print(f"Cloud cover: {item.properties.get('eo:cloud_cover')}%")

    output_dir = RAW_DIR / str(year)
    output_dir.mkdir(parents=True, exist_ok=True)

    for asset_name in REQUIRED:

        asset = item.assets.get(asset_name)

        if asset is None:
            print(f"  MISSING ASSET: {asset_name}")
            continue

        href = asset.href
        parsed = urlparse(href)

        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        filename = Path(key).name
        output = output_dir / filename

        download_with_retry(bucket, key, output)


print()
print("=" * 70)
print("CHECKING PLQ FILES")
print("=" * 70)

for year in [2018, 2020, 2022, 2024]:

    folder = RAW_DIR / str(year)

    files = list(folder.glob("T32PLQ_*")) if folder.exists() else []

    print(f"{year}: {len(files)} PLQ files")

print()
print("Expected: 7 PLQ files for each year.")
