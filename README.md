# Spatiotemporal Analysis and Machine Learning-Based Prediction of Land Use/Land Cover Change in Abuja, Nigeria

## Project Overview

This project investigates spatiotemporal Land Use/Land Cover (LULC) patterns in Abuja, Nigeria using Sentinel-2 satellite imagery, spectral indices, GIS preprocessing and Random Forest machine learning.

Historical LULC classifications were produced for:

- 2018
- 2020
- 2022
- 2024

An exploratory 2026 baseline scenario was subsequently generated using transition probabilities derived from the 2022–2024 period.

The project demonstrates an end-to-end geospatial machine-learning workflow covering satellite-image preprocessing, feature engineering, classification, accuracy assessment, area estimation, change detection, transition analysis and scenario modelling.

---

## Objectives

The project aims to:

1. Prepare multi-temporal Sentinel-2 imagery for LULC analysis.
2. Generate spectral and derived features for classification.
3. Develop Random Forest LULC classifiers.
4. Produce year-specific LULC maps.
5. Estimate LULC class areas and proportions.
6. Quantify temporal LULC changes and class transitions.
7. Develop an exploratory 2026 baseline scenario.
8. Document methodological limitations and opportunities for future improvement.

---

## LULC Classes

| Code | Class |
|---:|---|
| 1 | Built-up area |
| 2 | Vegetation |
| 3 | Bare land |
| 4 | Water |
| 5 | Cropland |

---

## Data and Features

The analysis uses Sentinel-2 Level-2A imagery covering the study area.

The classification feature stack contains:

- B02 — Blue
- B03 — Green
- B04 — Red
- B08 — Near Infrared
- B11 — Shortwave Infrared 1
- B12 — Shortwave Infrared 2
- NDVI — Normalized Difference Vegetation Index
- NDBI — Normalized Difference Built-up Index
- NDWI — Normalized Difference Water Index

The imagery was mosaicked, clipped to the study area, resampled to a common 10 m grid and masked using the Sentinel-2 Scene Classification Layer.

---

## Methodology

The main workflow is:

```text
Sentinel-2 imagery
       ↓
Tile mosaicking
       ↓
Cloud / invalid-pixel masking
       ↓
Spatial resampling
       ↓
Spectral indices
       ↓
Feature stacks
       ↓
Training samples
       ↓
Random Forest classification
       ↓
Accuracy assessment
       ↓
LULC maps
       ↓
Area statistics
       ↓
Change detection
       ↓
Transition analysis
       ↓
2026 baseline scenario