# Results and Interpretation

## 1. Overview

This section presents the results of the spatiotemporal Land Use/Land Cover (LULC) analysis for Abuja, Nigeria. LULC classifications were produced for 2018, 2020, 2022, and 2024 using Sentinel-2 imagery and Random Forest classification. The analysis included classification assessment, area statistics, change detection, transition analysis, and an exploratory 2026 baseline scenario.

The five mapped classes were:

1. Built-up area
2. Vegetation
3. Bare land
4. Water
5. Cropland

---

## 2. LULC Classification Results

The year-specific classifications produced the following class proportions:

| Year | Built-up | Vegetation | Bare land | Water | Cropland |
|---|---:|---:|---:|---:|---:|
| 2018 | 31.24% | 13.37% | 29.07% | 0.61% | 25.71% |
| 2020 | 32.76% | 13.14% | 29.94% | 0.40% | 23.75% |
| 2022 | 33.07% | 9.64% | 31.94% | 0.48% | 24.86% |
| 2024 | 38.48% | 7.66% | 30.25% | 0.40% | 23.21% |

The mapped proportion of built-up land increased between 2018 and 2024, while vegetation and cropland decreased. Bare land remained a substantial component of the mapped landscape throughout the study period.

---

## 3. Classification Accuracy

The 2024 classification was evaluated using both random and spatial validation.

### Random validation

- Overall accuracy: **79.40%**
- Cohen's kappa: **0.7425**

### Spatial block validation

- Overall accuracy: **82.67%**
- Cohen's kappa: **0.7734**

The spatial validation results were:

| Class | Precision | Recall | F1-score |
|---|---:|---:|---:|
| Built-up | 0.697 | 0.628 | 0.661 |
| Vegetation | 0.799 | 0.830 | 0.815 |
| Bare land | 0.721 | 0.763 | 0.741 |
| Water | 0.996 | 0.997 | 0.996 |
| Cropland | 0.695 | 0.696 | 0.696 |

Water was the most clearly separated class. Greater confusion occurred among Built-up, Bare land, and Cropland.

The most influential variables in the spatial Random Forest model included B04, NDVI, B08, and NDWI.

### Important validation limitation

The validation labels were derived from the 2024 reference classification rather than independent field observations. Therefore, these accuracy values should be interpreted as model-performance diagnostics rather than fully independent historical accuracy estimates.

---

## 4. LULC Area Changes: 2018–2024

The mapped areas were:

| Class | 2018 area (km²) | 2024 area (km²) | Net difference (km²) |
|---|---:|---:|---:|
| Built-up | 214.63 | 270.49 | +55.87 |
| Vegetation | 91.87 | 53.87 | -38.00 |
| Bare land | 199.74 | 212.62 | +12.88 |
| Water | 4.18 | 2.81 | -1.37 |
| Cropland | 176.68 | 163.15 | -13.53 |

The largest increase in mapped area occurred for Built-up land, while Vegetation showed the largest reduction.

These values represent differences between classified endpoints. They should not be interpreted as independently validated physical land-cover conversions.

---

## 5. Temporal LULC Dynamics

### 2018–2020

The mapped Built-up proportion increased from 31.24% to 32.76%.

Net area differences were:

- Built-up: +15.00 km²
- Vegetation: +0.26 km²
- Bare land: +10.11 km²
- Water: -1.35 km²
- Cropland: -10.18 km²

### 2020–2022

The period was characterized by a modeled reduction in Vegetation and increases in Bare land and Cropland.

Net area differences were:

- Built-up: -0.22 km²
- Vegetation: -25.24 km²
- Bare land: +11.76 km²
- Water: +0.52 km²
- Cropland: +5.99 km²

### 2022–2024

The largest modeled increase in Built-up land occurred during this period.

Net area differences were:

- Built-up: +41.09 km²
- Vegetation: -13.02 km²
- Bare land: -8.98 km²
- Water: -0.54 km²
- Cropland: -9.34 km²

---

## 6. LULC Transition Analysis

The largest 2018–2024 transitions were:

| Transition | Area (km²) |
|---|---:|
| Bare land → Built-up | 72.79 |
| Built-up → Bare land | 54.56 |
| Cropland → Built-up | 45.57 |
| Cropland → Bare land | 39.72 |
| Vegetation → Cropland | 33.54 |
| Bare land → Cropland | 26.21 |
| Built-up → Cropland | 24.45 |

A major feature of the transition analysis is the substantial two-way exchange between Built-up and Bare land.

This pattern is important because the classification assessment also identified spectral overlap between these classes. Some mapped transitions may therefore reflect classification uncertainty rather than actual physical conversion.

---

## 7. Change Detection

The proportion of pixels assigned to a different class between successive classified maps was:

| Period | Classified changed pixels |
|---|---:|
| 2018–2020 | 43.76% |
| 2020–2022 | 41.05% |
| 2022–2024 | 40.78% |
| 2018–2024 | 51.06% |

These values describe changes in classified land-cover assignments. They should not be interpreted as independently verified physical land-cover change.

The high level of classified change is influenced by transitions involving Built-up, Bare land, Cropland, and Vegetation.

---

## 8. 2026 Baseline Scenario

A transition-based baseline scenario was generated using the observed 2022–2024 transition probabilities.

The resulting 2026 scenario was:

| Class | 2024 area (km²) | 2026 baseline (km²) | Net change (km²) |
|---|---:|---:|---:|
| Built-up | 270.49 | 288.63 | +18.14 |
| Vegetation | 53.87 | 46.48 | -7.39 |
| Bare land | 212.62 | 211.02 | -1.60 |
| Water | 2.81 | 2.51 | -0.29 |
| Cropland | 163.15 | 154.29 | -8.85 |

The corresponding class proportions were:

| Class | 2024 | 2026 baseline |
|---|---:|---:|
| Built-up | 38.48% | 41.06% |
| Vegetation | 7.66% | 6.61% |
| Bare land | 30.25% | 30.02% |
| Water | 0.40% | 0.36% |
| Cropland | 23.21% | 21.95% |

The baseline scenario therefore produces a modeled increase in Built-up land accompanied by modeled reductions in Vegetation and Cropland.

### Interpretation

The 2026 result is an exploratory transition-based baseline scenario rather than a validated prediction of future land cover.

It assumes that the transition structure observed between 2022 and 2024 provides a useful basis for constructing a 2026 scenario. Actual future land-cover dynamics may differ because of changes in development patterns, environmental conditions, infrastructure, policy, population, or other factors not explicitly represented in the transition model.

---

## 9. Overall Interpretation

The classification results indicate a modeled increase in the proportion and area of Built-up land between 2018 and 2024, accompanied by reductions in mapped Vegetation and Cropland.

The transition analysis identifies Bare land → Built-up, Built-up → Bare land, and Cropland → Built-up among the dominant modeled transitions.

The substantial two-way exchange between Built-up and Bare land is particularly important when interpreting the results. The spectral similarity between these classes creates potential classification uncertainty, meaning that not every mapped transition necessarily represents a physical change on the ground.

The 2026 baseline scenario extends the recent transition structure forward and produces a modeled increase in Built-up land from 270.49 km² in 2024 to 288.63 km² in the baseline scenario.

This result should be interpreted as an exploratory scenario that demonstrates how recent transition patterns can be propagated forward, rather than as a definitive statement about Abuja's future land-cover composition.

---

## 10. Key Findings

The major findings of the analysis are:

1. Built-up land increased from 31.24% of the mapped area in 2018 to 38.48% in 2024.
2. Vegetation decreased from 13.37% to 7.66% over the same classified period.
3. Cropland decreased from 25.71% to 23.21%.
4. Bare land remained a major land-cover class throughout the study period.
5. The 2024 spatial validation produced an overall accuracy of 82.67% and a Cohen's kappa of 0.7734.
6. Built-up, Bare land, and Cropland showed greater classification difficulty than Water.
7. Bare land → Built-up was the largest modeled 2018–2024 transition at 72.79 km².
8. Built-up → Bare land was the second-largest modeled transition at 54.56 km².
9. The large two-way Built-up/Bare land transitions highlight an important classification uncertainty.
10. The 2026 baseline scenario produces a modeled increase in Built-up land to 288.63 km².

---

## 11. Interpretation Caveat

The results should be understood within the methodological limitations of the project.

Historical classifications were generated using year-specific models trained from pseudo-labels derived from the 2024 reference classification. Consequently, the historical results provide a useful analytical demonstration of the workflow but do not constitute fully independent historical ground-truth validation.

Similarly, the 2026 scenario is exploratory and transition-based. It should not be interpreted as a precise forecast.

Future work should incorporate independent reference data, field observations, spatially stratified validation, additional environmental and socioeconomic drivers, and more advanced spatial prediction approaches.