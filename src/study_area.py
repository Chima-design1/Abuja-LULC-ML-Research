from pathlib import Path

from project_config import PROJECT_ROOT


# Approximate Abuja study-area bounding box.
# Coordinates are in decimal degrees.
STUDY_AREA = {
    "name": "Abuja, Nigeria",
    "min_longitude": 7.20,
    "min_latitude": 8.80,
    "max_longitude": 7.65,
    "max_latitude": 9.15,
}


def main():
    print("Abuja study area")
    print("=" * 30)

    for key, value in STUDY_AREA.items():
        print(f"{key}: {value}")

    print()
    print(f"Configuration location: {PROJECT_ROOT / 'src' / 'study_area.py'}")


if __name__ == "__main__":
    main()
