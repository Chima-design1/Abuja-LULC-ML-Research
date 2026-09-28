from pathlib import Path
from urllib.parse import urlparse
import os
import time
import boto3
from pystac_client import Client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

STAC_URL = "https://stac.dataspace.copernicus.eu/v1"
S3_ENDPOINT = "https://eodata.dataspace.copernicus.eu"

REQUIRED_ASSETS = [
    "B02_10m",
    "B03_10m",
    "B04_10m",
    "B08_10m",
    "B11_20m",
    "B12_20m",
    "SCL_20m",
]

SCENES = {
    2018: [
        "S2B_MSIL2A_20180128T095239_N0500_R079_T32PLQ_20230824T195825",
    ],
    2020: [
        "S2A_MSIL2A_20200113T095351_N0500_R079_T32PLQ_20230428T210929",
    ],
    2022: [
        "S2A_MSIL2A_20220122T095321_N0510_R079_T32PLQ_20240504T045544",
    ],
    2024: [
        "S2A_MSIL2A_20240122T095311_N0510_R079_T32PLQ_20240122T132047",
    ],
}

access_key = os.environ.get("CDSE_S3_ACCESS_KEY")
secret_key = os.environ.get("CDSE_S3_SECRET_KEY")

if not access_key or not secret_key:
    raise RuntimeError("CDSE S3 credentials are missing.")

catalog = Client.open(STAC_URL)

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="default",
)

MAX_RETRIES = 5

def download_with_retry(bucket, key, output_file):

    if output_file.exists():
        print(f"  SKIP: {output_file.name}")
        return True

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            print(
                f"  Downloading {output_file.name} "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            s3.download_file(
                bucket,
                key,
                str(output_file),
            )

            size_mb = output_file.stat().st_size / (1024 * 1024)

            print(
                f"  DONE: {output_file.name} "
                f"({size_mb:.1f} MB)"
            )

            return True

        except Exception as e:

            print(
                f"  WARNING: attempt {attempt} failed: "
                f"{type(e).__name__}: {e}"
            )

            if output_file.exists():
                output_file.unlink()

            if attempt < MAX_RETRIES:
                wait = attempt * 10
                print(f"  Waiting {wait} seconds before retry...")
                time.sleep(wait)

    print(f"  FAILED permanently: {output_file.name}")
    return False


print("=" * 70)
print("ABUJA LULC - T32PLQ DOWNLOAD")
print("=" * 70)

downloaded = 0
skipped = 0
failed = 0

for year, scene_ids in SCENES.items():

    print()
    print("=" * 70)
    print(f"YEAR: {year}")
    print("=" * 70)

    year_dir = RAW_DIR / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)

    for scene_id in scene_ids:

        print()
        print(f"Scene: {scene_id}")

        try:
            items = list(
                catalog.search(
                    collections=["sentinel-2-l2a"],
                    ids=[scene_id],
                ).items()
            )

            if not items:
                print("  ERROR: Scene not found.")
                failed += 1
                continue

            item = items[0]

            print(f"  Date: {item.datetime}")
            print(
                f"  Cloud cover: "
                f"{item.properties.get('eo:cloud_cover')}%"
            )

            for asset_name in REQUIRED_ASSETS:

                if asset_name not in item.assets:
                    print(f"  ERROR: Missing {asset_name}")
                    failed += 1
                    continue

                href = item.assets[asset_name].href

                parsed = urlparse(href)

                if parsed.scheme != "s3":
                    print(f"  ERROR: Unexpected URL: {href}")
                    failed += 1
                    continue

                bucket = parsed.netloc
                key = parsed.path.lstrip("/")
                filename = Path(key).name
                output_file = year_dir / filename

                if output_file.exists():
                    print(f"  SKIP: {filename}")
                    skipped += 1
                    continue

                success = download_with_retry(
                    bucket,
                    key,
                    output_file,
                )

                if success:
                    downloaded += 1
                else:
                    failed += 1

        except Exception as e:
            print(
                f"  ERROR processing scene: "
                f"{type(e).__name__}: {e}"
            )
            failed += 1


print()
print("=" * 70)
print("T32PLQ DOWNLOAD FINISHED")
print("=" * 70)
print(f"Downloaded: {downloaded}")
print(f"Skipped:    {skipped}")
print(f"Failed:     {failed}")

print()
print("Files currently present:")

for year in [2018, 2020, 2022, 2024]:

    folder = RAW_DIR / str(year)

    if folder.exists():

        files = list(folder.glob("*_T32PLQ_*"))

        print(f"{year}: {len(files)} PLQ files")

print()
print("Next step: merge/clip T32PLR + T32PLQ and begin preprocessing.")
