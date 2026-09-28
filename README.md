# Abuja Land Use/Land Cover Change Analysis

A reproducible geospatial machine-learning study of land use/land cover (LULC) patterns in the Abuja study area, Nigeria, using Sentinel-2 imagery for 2018, 2020, 2022 and 2024. The repository contains the analysis code, report, documentation, selected figures and lightweight numerical results.

## Research objectives

- Prepare comparable Sentinel-2 observations and spectral features for four study years.
- Classify five LULC classes with year-specific Random Forest models.
- Assess 2024 model agreement using random and spatial block validation.
- Summarize mapped class areas, changes and transitions from 2018 to 2024.
- Demonstrate an exploratory, quantity-constrained 2026 transition-based baseline scenario.

## Study area

The study polygon covers part of the Federal Capital Territory around Abuja, approximately 7.20°E–7.65°E and 8.80°N–9.15°N. Processing uses WGS 84 / UTM Zone 32N (EPSG:32632) and a 10 m analysis grid. Reported areas describe valid classified pixels within the study mask.

## LULC classes

| Code | Class |
|---:|---|
| 0 | Built-up |
| 1 | Vegetation |
| 2 | Bare land |
| 3 | Water |
| 4 | Cropland |

## Data sources and features

The study uses Sentinel-2 Level-2A surface-reflectance imagery from the Copernicus Data Space Ecosystem. Six spectral bands are used: B02 (blue), B03 (green), B04 (red), B08 (near infrared), B11 (shortwave infrared 1) and B12 (shortwave infrared 2). Three derived features are NDVI, NDBI and NDWI. The 20 m bands are resampled to a common 10 m grid; mosaicking, study-area clipping and Scene Classification Layer masking are part of preprocessing.

Raw imagery, local boundaries, training samples, intermediate stacks and generated raster outputs are excluded from the repository. They must be obtained or generated locally before rerunning workflows.

## Methodology and classification

The workflow covers data acquisition, mosaicking and masking, feature engineering, training-sample generation, year-specific Random Forest classification, accuracy assessment, area estimation, change detection and transition analysis. The model uses 300 trees, square-root feature selection, a minimum leaf size of 2 and random state 42. See [methodology](documentation/METHODOLOGY.md) and the scripts in [src](src/).

Training labels for historical year-specific classifications are pseudo-labels derived from the 2024 reference classification. Thus, 2018–2022 results are not independent historical ground truth. The 2024 validation values measure agreement with available reference labels; they are not field-validated accuracy estimates.

## Accuracy assessment (2024)

| Validation design | Overall accuracy | Cohen's kappa |
|---|---:|---:|
| Random validation | 79.40% | 0.7425 |
| Spatial block validation | 82.67% | 0.7734 |

Spatial blocking reduces nearby train/validation overlap but does not make the reference labels independent. Details and class-level metrics are in [results interpretation](documentation/RESULTS_INTERPRETATION.md) and [results/accuracy](results/accuracy/).

## Key results

Verified class proportions from the published area-statistics CSV:

| Year | Built-up | Vegetation | Bare land | Water | Cropland |
|---|---:|---:|---:|---:|---:|
| 2018 | 31.24% | 13.37% | 29.07% | 0.61% | 25.71% |
| 2020 | 32.76% | 13.14% | 29.94% | 0.40% | 23.75% |
| 2022 | 33.07% | 9.64% | 31.94% | 0.48% | 24.86% |
| 2024 | 38.48% | 7.66% | 30.25% | 0.40% | 23.21% |

From 2018 to 2024, mapped Built-up rose from 214.63 to 270.49 km² (+55.87 km²); Vegetation fell from 91.87 to 53.87 km² (−38.00 km²); and Cropland fell from 176.68 to 163.15 km² (−13.53 km²). These are classified-map differences. Built-up/Bare land spectral overlap and pseudo-label dependence limit physical interpretation. The [results tables](results/) and [report figures](report_figures/) retain the supporting evidence.

## 2026 baseline scenario

The scenario applies transition probabilities estimated from the 2022–2024 transition matrix to 2024 class quantities, then assigns pixels in descending transition-probability order with deterministic source/destination and raster-row-order tie-breaking. It is exploratory, quantity-constrained and transition-based; it does not use location-specific suitability scores or drivers and is not a definitive spatial forecast. It does not model independent development drivers or validate future outcomes. See [scenario outputs](results/prediction_2026/) and [limitations](documentation/LIMITATIONS.md).

## Limitations

Important limitations include pseudo-labels derived from the 2024 reference classification for historical years, no comprehensive independent field reference dataset, confusion among Built-up, Bare land and Cropland, variation between image dates, and a simplified 2026 baseline without explicit socioeconomic, planning or environmental drivers. Mapped changes should not be equated with independently verified land conversion.

## Reproducibility

Use Python 3.10 or newer and install the dependencies listed in [requirements.txt](requirements.txt). From the repository root:

```bash
python -m venv .venv
# Activate the environment, then:
python -m pip install -r requirements.txt
python src/test_project_setup.py
```

The setup check only verifies local prerequisites. The workflow scripts expect data and generated inputs in the paths defined by the scripts and configuration; these large/private inputs are not bundled. Obtain Sentinel-2 data and the study boundary, place them in the expected local directories, and run the relevant scripts in sequence. Inspect each script's input/output paths before execution. Existing CSV results are provided for review; reproducing them requires the omitted inputs. See [data documentation](documentation/MAPS_AND_DATA.md). The QGIS project is included, but may rely on local layers.

## Repository structure

```text
documentation/   Methods, results interpretation, limitations, data notes
notebooks/       Setup notebook
report_figures/  Selected report-ready maps and plots
reports/         Final Markdown report
results/         Lightweight accuracy, area, change and transition tables
src/             Python acquisition, preprocessing, classification and analysis scripts
Abuja_LULC_Analysis.qgz
README.md
requirements.txt
```

## Software and tools

Python, NumPy, Pandas, Rasterio, GeoPandas, Shapely, scikit-learn, Matplotlib, QGIS and Git/GitHub. Exact Python package dependencies are listed in requirements.txt.

## Project status

Research portfolio project; historical results, interpretation caveats and the exploratory 2026 baseline are documented. Independent year-specific reference data and stronger validation remain future work.
