import json

from project_config import RAW_DATA_DIR
from study_area import STUDY_AREA


def create_geojson():
    coordinates = [
        [
            [STUDY_AREA["min_longitude"], STUDY_AREA["min_latitude"]],
            [STUDY_AREA["max_longitude"], STUDY_AREA["min_latitude"]],
            [STUDY_AREA["max_longitude"], STUDY_AREA["max_latitude"]],
            [STUDY_AREA["min_longitude"], STUDY_AREA["max_latitude"]],
            [STUDY_AREA["min_longitude"], STUDY_AREA["min_latitude"]],
        ]
    ]

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": STUDY_AREA["name"]
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
            }
        ]
    }

    output_file = RAW_DATA_DIR / "abuja_study_area.geojson"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(geojson, file, indent=2)

    print("Study-area GeoJSON created successfully.")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    create_geojson()
