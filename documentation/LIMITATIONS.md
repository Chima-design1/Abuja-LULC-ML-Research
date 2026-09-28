# Limitations

## 1. Historical Reference Labels

The historical year-specific classifications were generated using pseudo-labels derived from the 2024 reference classification. Therefore, the 2018, 2020, and 2022 validation results should be interpreted as diagnostic model-performance measures rather than fully independent historical accuracy assessments.

## 2. Built-up and Bare Land Confusion

Built-up and Bare land displayed substantial spectral overlap. This is reflected in both the classification confusion matrices and the large two-way Built-up/Bare land transitions.

Consequently, some mapped transitions may represent classification uncertainty rather than physical land-cover conversion.

## 3. Independent Ground Truth

The project does not currently include comprehensive field-based or independently interpreted historical reference data. Independent reference samples would strengthen the accuracy assessment and historical change estimates.

## 4. Temporal Domain Shift

Sentinel-2 observations from different years can exhibit differences in atmospheric conditions, surface conditions, illumination, phenology, and sensor processing characteristics. Year-specific models were therefore used rather than applying a single model across all years.

## 5. Spatial Validation

Spatial block validation was introduced for the 2024 model to reduce the effects of spatial dependence between training and validation samples. However, the validation labels themselves were still derived from the reference classification and therefore are not equivalent to independent field validation.

## 6. Water Class Sample Support

Some historical validation sets contained fewer water samples than other classes. Consequently, very high water-class performance should be interpreted with consideration of the available validation support.

## 7. 2026 Baseline Scenario

The 2026 result is an exploratory transition-based baseline scenario. It assumes that the transition structure observed between 2022 and 2024 provides a useful basis for estimating a future scenario.

The scenario does not explicitly model population growth, road expansion, zoning, economic development, environmental constraints, infrastructure projects, or other socioeconomic and physical drivers.

Therefore, the 2026 output should not be interpreted as a definitive forecast.

## 8. Change Detection Interpretation

The reported percentage of changed pixels represents changes in classified land-cover assignments. It should not be interpreted directly as independently verified physical land-cover change.

## 9. Recommended Future Improvements

Future versions of the project should incorporate:

- Independent historical reference samples
- Field/GPS observations
- Spatially stratified validation
- Object-based image analysis
- Sentinel-1 SAR data
- DEM and terrain variables
- Road and accessibility variables
- Population and settlement data
- Protected-area constraints
- More advanced spatial Markov or cellular automata approaches
- Longer temporal image series
- Uncertainty and confidence mapping