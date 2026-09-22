# Application architecture

## Components

| Component | Responsibility | Boundary |
|---|---|---|
| `app.py` | Data-source selection, image verification, session edits, chart/table and download | No physical sensor integration or persistent server database |
| `thermal_analysis/model.py` | Immutable `Zone`, CSV/filename parsing, validation, proxy calculation, bands, safe CSV serialization | Standard library only; independently testable |
| `data/example_observations.csv` | Three transcribed records and explicit assumptions | Not the full experimental dataset |
| `tests/` | Numerical, invalid-input and interaction regression checks | Software validation, not physical validation |
| `scripts/package_release.py` | Explicit public-file allowlist and upload ZIP | Does not push to GitHub or rewrite Git history |

## Data contract

CSV requires `zone`, `average_c`, `maximum_c`, `minimum_c`, `material`, `u_value`, `area_m2`, `reference_c`, and `reference_basis`; `note` is optional. Reference basis is `indoor_air`, `outdoor_air` or `other`. Use a distinct zone label for every observation, including separate trials. Inputs must be finite, positive where appropriate and internally consistent. Unknown filename material IDs are rejected instead of silently substituted.

The parser rejects the entire CSV when a row fails, with a row-specific message; it does not silently omit invalid measurements. Original raw data stays in the local archive. To correct a reading, the user must verify the source and provide a new valid input file.

## Update and export flow

The app hashes the selected dataset to isolate edits between uploads. Material/area/note edits are applied through a form before all result rows are calculated. One `analyze()` function provides both detail metrics and overview data. Severity depends on the unrounded density proxy and therefore does not change simply because the area changes.

The filter affects the chart and visible table. Export always contains all observations, current assumptions, notes, flags and scenario hours. Formula-like text is escaped on export to reduce accidental spreadsheet evaluation. Downloaded CSV files can be reimported; derived columns are ignored and calculations are performed again.

Edits and flags are browser-session state. They are not saved to disk automatically, shared across users, or stored as longitudinal monitoring records. Export is the persistence mechanism currently available.
