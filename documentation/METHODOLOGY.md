# Abuja LULC Machine Learning Project — Methodology

## 1. Study Design

The workflow uses Sentinel-2 imagery for four historical study years: 2018, 2020, 2022 and 2024.

The processing chain consists of:

1. Study-area definition
2. Sentinel-2 acquisition
3. Image mosaicking
4. Cloud and invalid-pixel masking
5. Spatial resampling
6. Spectral feature construction
7. Training-sample generation
8. Random Forest classification
9. Accuracy assessment
10. Area estimation
11. Change detection
12. Transition analysis
13. 2026 baseline scenario generation

## 2. Sentinel-2 Data

Sentinel-2 Level-2A imagery was selected for the study years using dry-season scenes with very low reported cloud cover.

The workflow uses:

- B02 — Blue
- B03 — Green
- B04 — Red
- B08 — Near Infrared
- B11 — Shortwave Infrared 1
- B12 — Shortwave Infrared 2
- SCL — Scene Classification Layer

The two Sentinel-2 tiles covering the study area were mosaicked before clipping to the Abuja study boundary.

## 3. Preprocessing

The preprocessing workflow:

- mosaics the required Sentinel-2 tiles;
- clips imagery to the study area;
- converts reflectance to scaled values;
- resamples the 20 m bands to the 10 m analysis grid;
- resamples the Scene Classification Layer using nearest-neighbour resampling;
- masks invalid pixels using selected SCL classes;
- calculates spectral indices;
- creates a nine-band feature stack.

The final feature stack contains:

1. B02
2. B03
3. B04
4. B08
5. B11
6. B12
7. NDVI
8. NDBI
9. NDWI

## 4. Spectral Indices

### NDVI

Normalized Difference Vegetation Index was used to characterize vegetation response.

### NDBI

Normalized Difference Built-up Index was included as a built-up-related spectral feature.

### NDWI

Normalized Difference Water Index was included to improve separation of water and other land-cover classes.

## 5. Training Samples

Training labels were generated from the 2024 reference classification and sampled against the corresponding year-specific feature stacks.

The year-specific approach was adopted after applying a single 2024 model across earlier imagery produced substantial temporal domain-shift effects.

Training and validation samples were separated for each year.

## 6. Random Forest Classification

Random Forest classifiers were used because they can model nonlinear relationships among multiple spectral and derived features.

The principal model configuration used:

- 300 trees
- `max_features = sqrt`
- `min_samples_leaf = 2`
- `random_state = 42`

Separate year-specific models were developed for 2018, 2020 and 2022.

The 2024 classification used the spatial-validation workflow.

## 7. Accuracy Assessment

Two forms of 2024 assessment were performed.

### Random Holdout Validation

A conventional random validation subset was used to calculate:

- overall accuracy
- Cohen's kappa
- class precision
- class recall
- class F1-score
- confusion matrix

### Spatial Holdout Validation

Spatial blocks were used to reduce the potential effect of spatial autocorrelation between training and validation samples.

The spatial validation used approximately 2 km blocks, with a subset of blocks reserved for validation.

The resulting spatial validation metrics were interpreted cautiously because the labels originate from the 2024 reference classification rather than comprehensive independent field observations.

## 8. Area Estimation

Class areas were calculated from classified 10 m pixels.

Each valid pixel represents approximately:

**0.0001 km²**

Class area was calculated from the number of valid pixels belonging to each LULC class.

## 9. Change Detection

Pairwise change maps were generated for:

- 2018–2020
- 2020–2022
- 2022–2024
- 2018–2024

Pixels were classified as either unchanged or changed according to their class transition.

## 10. Transition Analysis

Transition matrices were generated to quantify movement between LULC classes.

For each period, the analysis identifies transitions such as:

- Built-up → Bare land
- Bare land → Built-up
- Cropland → Built-up
- Vegetation → Cropland
- Cropland → Bare land

Transition areas were also calculated in square kilometres and as percentages of the originating class.

## 11. 2026 Baseline Scenario

A transition-probability approach was used to construct an exploratory 2026 baseline scenario.

Transition probabilities were derived from the 2022–2024 transition matrix.

Expected 2026 class quantities were calculated from the 2024 class quantities and transition probabilities. Pixels were assigned to meet these targets in descending source-to-destination probability order. Equal-probability candidates follow deterministic source/destination iteration and raster row-order tie-breaking. No location-specific suitability score or spatial driver is used. The result is a quantity-constrained baseline scenario, not a definitive spatial forecast.

Transition probabilities are estimated from 2022–2024. The resulting 2026 map is an exploratory, quantity-constrained, transition-based baseline scenario; deterministic allocation produces a spatial illustration but does not establish where future development will occur.

## 12. Reproducibility

The principal processing and analysis scripts are located in `src/`.

Lightweight numerical outputs are provided under `results/`.

Large Sentinel-2 datasets, intermediate raster stacks and trained model binaries are retained locally and excluded from the public repository.
