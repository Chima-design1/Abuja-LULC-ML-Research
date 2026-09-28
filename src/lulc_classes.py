LULC_CLASSES = {
    1: "Built-up area",
    2: "Vegetation",
    3: "Bare land",
    4: "Water",
    5: "Cropland",
}


def main():
    print("Abuja LULC classification classes")
    print("=" * 40)

    for class_id, class_name in LULC_CLASSES.items():
        print(f"{class_id}: {class_name}")


if __name__ == "__main__":
    main()
