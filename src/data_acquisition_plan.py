STUDY_YEARS = [2018, 2020, 2022, 2024]

DATA_ACQUISITION_PLAN = {
    year: {
        "sensor": "Sentinel-2",
        "target": "Abuja, Nigeria",
        "preferred_period": "Dry season",
        "cloud_cover_target": "Preferably below 20%",
        "status": "Not acquired",
    }
    for year in STUDY_YEARS
}


def main():
    print("Abuja LULC data-acquisition plan")
    print("=" * 45)

    for year, details in DATA_ACQUISITION_PLAN.items():
        print(f"\nYear: {year}")

        for key, value in details.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
