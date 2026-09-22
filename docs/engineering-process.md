# Engineering process and development history

This narrative is reconstructed from the retained course reports, status reports, presentation, attribution tables and source snapshots. It distinguishes observed evidence from design intentions. Dates in some drafts differ; the sequence below is more reliable than assigning an exact completion date to every document.

## 1. Establish the need and scope

The January–February 2026 work included research planning, client communication and site visits. The first client meeting is recorded for February 4. A February 6 visit recorded the main entrance, vestibule, glazing dimensions and temperatures. The problem was the absence of a practical means to locate, quantify and display potential heat-loss zones for the Galbraith living lab.

The scope narrowed to the first-floor main entrance: accessible for student measurements and containing glazing, metal framing and frequently operated doors. Laboratories and offices presented access and occupancy constraints. The team identified the Sustainability Office, Facilities and Services, and Environmental Health & Safety as relevant stakeholders.

The PR established three functions: detect locations, quantify severity and display organized results. Targets included repeatable measurements, three severity levels, novice usability, transfer to another building, a CAD 200 system budget, privacy and seasonal operation. These are requirements, not evidence that every target was met.

## 2. Generate and screen concepts

The CDS reports 127 means generated using brainstorming, morphological charts, analogy and SCAMPER. A means is a possible way to perform a function, not necessarily a complete system. The idea workbook retains exploratory, sometimes impractical proposals; these were part of divergence, not implemented products.

Duplicate removal, feasibility screening, multivoting and a graphical decision chart narrowed the options. Three systems were developed far enough for comparison:

| Concept | Detection | Processing and display | Main tradeoff |
|---|---|---|---|
| Mobile Thermal Imaging System | Phone-attached thermal camera, manual survey | Temperature/material data and website | Portable and intuitive; operator-dependent |
| Fixed Sensor Monitoring Network | Installed temperature sensors | Raspberry Pi, tabular time series and website | Repeatable sampling; installation and calibration burden |
| Drone-based Thermal Scanning System | Drone-mounted temperature device | Spatial samples and proposed thermal map | Automated coverage; navigation and operational complexity |

## 3. Select and integrate the solution

The CDS used a Pugh comparison to recommend the mobile thermal system for its balance of usability, portability and feasibility. The retained documents do not establish that all three systems were physically constructed or that a budget was verified with receipts.

Integration meant combining selected functional components: a portable camera for detection, manually transcribed measurements and material assumptions for calculation, and a web dashboard for communication. There is no evidence of a final hybrid drone-plus-sensor-plus-camera system. It would be misleading to describe concept comparison as physical integration of all three alternatives.

The proposed end-to-end architecture also included timestamped records, cloud storage, a spatial floor-plan map and automatic image privacy processing. The implemented prototype only partially realized that architecture. Its working path was image capture → filename/spreadsheet transcription → Python calculation → charts and CSV export.

## 4. Build and evaluate the prototype

The retained thermal images are associated with late-March surveying. The workbook records temperatures, material assumptions and normalized areas; the filename convention connects labelled images to the program. The prototype used Streamlit with Pandas and Plotly for inspection and visualization.

The final presentation compared door edges, glass doors, glass walls and a wall surface. It reported approximately 9.62% variation between trials and 75% agreement with expected ranking. These are documented presentation claims; the public release does not claim to reproduce them. The MoS planning document still contains an unfilled results placeholder, and the available workbook only contains explicit three-trial blocks for some locations.

## 5. Iterate the software

The source snapshots provide concrete evidence of software evolution:

| Snapshot | Observable change | Evidence boundary |
|---|---|---|
| 1.0 | Filename temperature parsing, material selection and overview charts | Baseline source exists |
| 1.1 | Material IDs in filenames, material reference table, EXIF orientation handling and chart adjustments | Compared directly with 1.0 |
| 1.2 | English comments and a header change | Compared directly with 1.1; not a major new algorithm |
| 2.0 | Area input, custom U-values, notes, flags, filtering, ranking, radar chart and CSV export | Source exists; no historic test suite was found |
| September 2026 publication revision | Shared validated model, CSV demo, consistent fixed bands, corrected state/update behavior, documented assumptions, tests and packaging | Changes made during repository preparation |

The release deliberately simplifies the charts to one interpretable comparison view and a complete data table. Historical radar and histogram code remains in the local archive and earlier Git history. Its removal is a presentation simplification, not evidence of a more accurate physical model.

## 6. Debug and verify the publication revision

Inspection of 2.0 found inconsistent standard-deviation conventions across views, area-sensitive severity classification, results calculated before edited values were applied, a histogram reference line in mismatched units, and unvalidated filename inputs. The release replaces duplicated calculations with a tested model, validates inputs before use and calculates all displayed outputs after form submission.

Tests provide software evidence for calculations and workflow behavior. They do not prove sensor calibration, actual envelope heat transfer, novice scan time, seasonal performance or retrofit savings. See [verification](verification.md).

## 7. Next engineering steps

1. Define a physically appropriate measurement protocol and separate transmission, infiltration and surface effects.
2. Verify assembly properties and camera emissivity/reflection settings; collect paired reference measurements.
3. Store complete repeated trials, timestamps, conditions and calibration records.
4. Add radiometric ingestion and persistent location-based history only after agreeing the data model.
5. Validate novice usability, another building and different seasons against the original requirements.

No new field experiment or building modification was performed during repository preparation.
