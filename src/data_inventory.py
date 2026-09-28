from pathlib import Path

from project_config import RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLES_DIR


def list_files(folder: Path):
    return sorted(
        item for item in folder.rglob("*")
        if item.is_file()
    )


def main():
    folders = {
        "Raw data": RAW_DATA_DIR,
        "Processed data": PROCESSED_DATA_DIR,
        "Samples": SAMPLES_DIR,
    }

    print("Abuja LULC data inventory")
    print("=" * 30)

    for name, folder in folders.items():
        files = list_files(folder)

        print(f"\n{name}")
        print(f"Location: {folder}")
        print(f"Files found: {len(files)}")

        if files:
            for file in files:
                print(f" - {file.relative_to(folder)}")
        else:
            print(" - No files yet")


if __name__ == "__main__":
    main()
