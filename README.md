# Galbraith Building Heat Loss Analysis

A Streamlit application that analyzes thermal camera data and estimates heat loss from different areas of a building.

## Overview

This project was developed to analyze thermal images collected from the University of Toronto's Galbraith Building.

The application reads temperature information from uploaded image filenames, assigns material properties, and estimates heat loss using a simple heat-transfer model.

## Features

* Upload multiple thermal images
* Read average, maximum, and minimum temperatures
* Select the material of each building zone
* Enter the surface area of each zone
* Use default or custom U-values
* Calculate heat loss per square metre
* Estimate total and annual heat loss
* Compare different building zones
* Display interactive charts
* Add notes and flag zones for further inspection
* Export results as a CSV file

## Heat-Loss Model

The program estimates heat loss using:

```text
Heat Loss = U × A × |ΔT|
```

where:

* `U` is the material U-value in W/m²K
* `A` is the surface area in m²
* `ΔT` is the difference between the surface and environmental temperatures

The annual energy-loss estimate is calculated using:

```text
Annual Energy Loss = Heat Loss × 8760 / 1000
```

## Technologies

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* Pillow

## Image Filename Format

The program reads temperature and material information from the image filename.

Use the following format:

```text
ZoneName(AverageTemperature MaximumTemperature MinimumTemperature MaterialID).png
```

Example:

```text
NorthWindow(12.4 15.2 9.8 2).png
```

In this example:

* Zone: `NorthWindow`
* Average temperature: `12.4°C`
* Maximum temperature: `15.2°C`
* Minimum temperature: `9.8°C`
* Material ID: `2`

The application includes a material ID reference table in the sidebar.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Galbraith-Building-Heat-Loss-Analysis.git
cd Galbraith-Building-Heat-Loss-Analysis
```

Install the required packages:

```bash
pip install streamlit pandas numpy plotly pillow
```

Run the application:

```bash
streamlit run app.py
```

Replace `app.py` with the actual name of the main Python file when necessary.

## Usage

1. Enter the environmental temperature.
2. Upload thermal images using the required filename format.
3. Select a building zone from the sidebar.
4. Confirm the material and enter the zone area.
5. Review the estimated heat-loss results.
6. Compare all zones on the overview page.
7. Export the results as a CSV report.

## Notes

The current version reads temperature values from image filenames rather than directly analyzing thermal-image pixels.

The heat-loss and annual-energy values are simplified estimates and are mainly intended for comparing different building zones.
