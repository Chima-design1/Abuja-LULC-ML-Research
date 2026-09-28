# Abuja LULC Machine Learning Project — Project Overview

## Project Title

**Spatiotemporal Analysis and Machine Learning-Based Prediction of Land Use/Land Cover Change in Abuja, Nigeria Using Sentinel-2 Data**

## Overview

This project investigates land use/land cover (LULC) patterns and changes within the Abuja study area using Sentinel-2 satellite imagery, spectral indices, GIS-based preprocessing, and Random Forest machine learning.

The analysis covers four historical study years:

- 2018
- 2020
- 2022
- 2024

A 2026 baseline scenario was subsequently generated using transition probabilities derived from the 2022–2024 period.

## LULC Classes

Five land-cover classes are used:

| Code | Class |
|---|---|
| 1 | Built-up area |
| 2 | Vegetation |
| 3 | Bare land |
| 4 | Water |
| 5 | Cropland |

## Main Objectives

1. Prepare multi-temporal Sentinel-2 imagery for LULC analysis.
2. Generate spectral and vegetation-related features.
3. Develop Random Forest classification models.
4. Produce year-specific LULC maps for 2018, 2020, 2022 and 2024.
5. Estimate class areas and proportions.
6. Quantify LULC changes and class-to-class transitions.
7. Develop an exploratory 2026 baseline scenario.
8. Document methodological limitations and opportunities for future improvement.

## Main Technologies

- Python
- QGIS
- Sentinel-2
- Rasterio
- GeoPandas
- NumPy
- Pandas
- scikit-learn
- Matplotlib
- Git/GitHub

## Repository Organization

- `src/` — processing, classification and analysis scripts
- `documentation/` — project documentation
- `reports/` — final academic report
- `results/` — lightweight numerical results for reproducibility and review
- `report_figures/` — figures used in the report
- `notebooks/` — notebook workspace
- `data/` — local geospatial datasets and intermediate data
- `outputs/` — generated raster and model outputs retained locally
- `Abuja_LULC_Analysis.qgz` — QGIS project

Large raw, processed and intermediate datasets are intentionally excluded from the public Git repository.

## Important Interpretation Note

Historical classifications were developed using year-specific models trained from labels derived from the 2024 reference classification. They therefore should not be interpreted as fully independent ground-truth classifications.

The 2026 result is an exploratory transition-based baseline scenario rather than a definitive forecast.
