DATA_REQUIREMENTS = {
    "Sentinel-2 imagery": "Satellite imagery for Abuja",
    "Study-area boundary": "Abuja GeoJSON boundary",
    "Cloud information": "Cloud cover percentage or cloud mask",
    "Acquisition dates": "Images from selected years or periods",
    "Training samples": "Labeled samples for the five LULC classes",
    "Validation samples": "Independent samples for accuracy assessment",
}


def main():
    print("Abuja LULC data-acquisition checklist")
    print("=" * 45)

    for item, description in DATA_REQUIREMENTS.items():
        print(f"[ ] {item}: {description}")


if __name__ == "__main__":
    main()
