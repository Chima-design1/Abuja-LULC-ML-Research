LULC_CLASSES = {
    0: "Built-up",
    1: "Vegetation",
    2: "Bare land",
    3: "Water",
    4: "Cropland",
}


def main():
    print("Abuja LULC classification classes")
    print("=" * 40)

    for class_id, class_name in LULC_CLASSES.items():
        print(f"{class_id}: {class_name}")


if __name__ == "__main__":
    main()
