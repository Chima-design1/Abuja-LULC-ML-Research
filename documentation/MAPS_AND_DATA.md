# Abuja LULC Machine Learning Project — Maps and Data

## 1. Data Sources

The project uses Sentinel-2 Level-2A imagery for:

- 2018
- 2020
- 2022
- 2024

The imagery was acquired from the Copernicus Data Space ecosystem.

## 2. Study Area

The local study-area boundary is stored in:

`data/raw/abuja_study_area.geojson`

The boundary uses geographic coordinates and is used to define the Abuja analysis extent.

## 3. Feature Data

Processed Sentinel-2 feature stacks are retained locally under:

`data/processed/`

These contain the six spectral bands and three derived indices used by the classification workflow.

Because these files are large, they are excluded from the public Git repository.

## 4. Classification Maps

Year-specific classified rasters are generated under:

`outputs/lulc_maps/`

The main historical maps are:

- `Abuja_LULC_2018_year_specific.tif`
- `Abuja_LULC_2020_year_specific.tif`
- `Abuja_LULC_2022_year_specific.tif`
- `Abuja_LULC_2024_year_specific.tif`

## 5. Change Maps

Change rasters are generated under:

`outputs/change_maps/`

Available periods include:

- 2018–2020
- 2020–2022
- 2022–2024
- 2018–2024

## 6. 2026 Baseline Scenario

The exploratory 2026 baseline raster is stored locally under:

`outputs/prediction_2026/`

The associated lightweight statistics are published under:

`results/prediction_2026/`

## 7. Figures

Report-ready figures are stored under:

`report_figures/`

These include:

- year-specific LULC maps;
- LULC area trends;
- net LULC change;
- dominant transitions;
- change maps;
- the 2026 baseline scenario.

## 8. Numerical Results

Selected lightweight numerical results are available under:

`results/`

### Accuracy

`results/accuracy/`

Contains the 2024 random and spatial validation metrics, classification reports, confusion matrices and feature importance tables.

### Area Statistics

`results/area_statistics/`

Contains year-specific LULC area statistics.

### Change Analysis

`results/change_analysis/`

Contains net class changes.

### Transition Analysis

`results/transition_analysis/`

Contains transition matrices and transition-area tables.

### 2026 Baseline

`results/prediction_2026/`

Contains the 2024–2026 baseline comparison and transition probabilities.

## 9. Large Data Policy

The public repository intentionally excludes:

- raw Sentinel-2 imagery;
- processed feature stacks;
- training-sample datasets;
- large raster exports;
- trained Random Forest `.joblib` models;
- temporary archives.

This keeps the repository lightweight while retaining the code, documentation, report, figures and numerical evidence required to understand and evaluate the project.

## 10. Interpretation

Maps and statistics should be interpreted together with `RESULTS_INTERPRETATION.md` and `LIMITATIONS.md`.

In particular, historical labels are derived from the 2024 reference classification and therefore do not represent fully independent field-validated ground truth for every historical year.
