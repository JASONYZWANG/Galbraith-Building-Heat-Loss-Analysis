# Methodology and interpretation

## What the application computes

The historical workflow uses:

```text
delta = abs(surface_average_c - reference_c)
screening_proxy_w_m2 = assumed_u_value * delta
area_scaled_proxy_w = screening_proxy_w_m2 * area_m2
constant_condition_scenario_kwh = area_scaled_proxy_w * hours / 1000
```

These equations preserve the arithmetic used in the course prototype while making its interpretation explicit. The reference may be indoor air, outdoor air or another user-specified condition. The example uses the workbook's 22.5°C indoor reference. Values calculated with different references should not be treated as directly equivalent observations.

An assembly U-value and an indoor/outdoor temperature difference can be used in a transmission model under appropriate assumptions. The prototype instead multiplies an assumed U-value by a surface/reference difference. That does not establish actual assembly heat flow. The published output is therefore called a screening proxy even though it carries W/m² and W units.

The model does not account for infiltration from door opening, wind, radiative exchange, thermal bridges, material segmentation, transient storage, surface emissivity or reflections. It does not infer insulation quality from a low band. A high value is a prompt for investigation, not a direct retrofit recommendation.

## Material assumptions

The retained example U-values are 5.7 for single glazing, 2.8 for double glazing and 5.7 for the metal door edge, in W/m²K. These reproduce project assumptions. The label "metal" alone cannot define the effective U-value of a complete door/frame assembly. They have not been measured for Galbraith.

The original broad material dictionary also contained values whose relationship to assembly U-values was unclear. The public filename importer retains only the three demonstrated IDs. CSV input supports other materials when users provide and document their own assumptions.

## Screening bands

This release adopts the presentation's fixed density thresholds, with explicit endpoints:

- Low: `0 <= proxy < 10 W/m²`.
- Medium: `10 <= proxy <= 50 W/m²`.
- High: `proxy > 50 W/m²`.

These are project-specific demonstration bands, not regulatory or generally validated building-performance thresholds. The historical workbook also contains mean ± 0.5 standard deviation bands; 2.0 applied relative bands to total W. Mixing these methods caused inconsistent interpretations. The release chooses one fixed method and records this change rather than rewriting the historic record.

## Area and energy

Sample areas are standardized to 1 m². The resulting W values describe assumed patches, not the full dimensions of the entrance or total building loss. Changing area changes the total proxy and scenario energy, but not the density band.

Scenario hours default to zero. A nonzero result assumes unchanged conditions throughout that duration. Even 8,760 hours does not make it a weather-based annual energy estimate. There is no heating schedule, weather series, HVAC efficiency or energy-meter validation in this model.

## Historical results

The presentation's repeatability and expected-trend agreement are separate concepts from physical accuracy. A stable measurement may still be biased, and agreement with an expectation is not calibration against a measured ground truth. No new field validation has been added in this release.
