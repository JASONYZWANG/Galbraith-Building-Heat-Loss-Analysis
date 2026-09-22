# Data provenance and unresolved source issues

## Published sample

`data/example_observations.csv` transcribes the root historical `Data Analysis.xlsx`, `Sheet1`, rows 7–9 (columns B–K). Glass door, glass wall and metal door-edge temperatures, assigned U-values, 1 m² areas and 22.5°C reference values are preserved. Labels were normalized for readability. Filenames in the original `Places` folder corroborate the average/maximum/minimum temperatures.

The sample contains no invented measurements. It omits timestamps: workbook rows have dates from March 28–31 while the raw image filenames consistently indicate March 29; the exact observation chronology cannot be reconciled from the retained files alone. The reference is labelled indoor air because workbook notes identify 22.5°C room temperature and 8°C outside temperature.

## Excluded and qualified data

| Source issue | Publication decision |
|---|---|
| Wall record average 22.8°C exceeds maximum 21.0°C | Exclude from runnable sample; do not guess a correction |
| Same wall described as brick and concrete, with U = 2 or 3; reference table also lists brick 2.1 | Retain discrepancy here; no definitive material assignment |
| MoS plan uses surface minus outside temperature; workbook uses 22.5°C room reference | Preserve workbook arithmetic; label it explicitly and qualify interpretation |
| Fixed and relative severity bands coexist | Release uses documented fixed bands |
| Demo script mentions door edge 51.9 W; workbook gives 66.12 W | Different reference settings can change output; canonical sample uses workbook inputs rather than mixing screenshots and tables |
| Presentation claims 9.62% variation and 75% trend agreement | Historical reported metrics only; not independently reproduced |
| Three trials explicitly retained for glass door and wall | Insufficient to reconstruct the complete claimed four-location trial analysis |

## Source map

Original files are retained locally, outside the publication package. This map allows the owner to audit the narrative without exposing private correspondence, signatures or student identifiers.

| Local archive source | What it supports |
|---|---|
| `Team 21 APS112/Galbraith_Heat_Loss_PR.docx` | Problem, scope, service environment, functions, objectives and constraints |
| `Team 21 APS112/Galbraith_Heat_Loss_CDS.docx` | Idea-generation method, alternatives, Pugh selection, proposed architecture and MoS plan |
| `Team 21 APS112/CDS Idea list.xlsx` | Exploratory ideas and selection working material |
| `Team 21 APS112/Status report/` | Research roles, visits, reporting and milestones |
| `Team 21 APS112/FP/Presentation Script.docx` and final PPTX | Demonstration narrative, reported outcomes and limitations |
| Attribution tables | Shared authorship and specific contributor activities |
| `Data Analysis.xlsx`, `Places/`, `thermal images/` | Measurements, annotations and calculation examples |
| `thermal_analyzer 1.0.py` through `2.0.py` | Direct evidence of code evolution |
| `Team 21 APS112/FP/MOS/` | Additional prototype snapshots and supporting experiment files |
| Videos and slide screenshots | Historical demonstration artifacts, not proof of deployed service |

The local archive includes a SHA-256 manifest of all 133 original files. Original contents were preserved during reorganization. Public summaries are editorial reconstructions; the course documents were not rewritten to manufacture a cleaner history.
