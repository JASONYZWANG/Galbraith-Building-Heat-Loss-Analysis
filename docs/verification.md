# Debugging and verification record

## Defects identified during publication preparation

These findings were obtained by source inspection in September 2026. They are not claimed to be bugs that the student team historically discovered or fixed.

| Finding in archived source or data | Release change | Regression evidence |
|---|---|---|
| Overview used sample standard deviation; detail used population standard deviation | Replace both with one fixed-band function | Boundary tests and consistent UI metrics |
| Severity in 2.0 depended on total W, mixing area and density | Classify the density proxy only | Area scaling test |
| Detail severity was computed before updated material/area inputs | Apply form edits before calculating any output | UI edit/submission test |
| Histogram density axis used a total-W mean reference line | Replace with a single density comparison chart | Shared chart/table source |
| Unknown material IDs silently defaulted to first material | Reject unsupported IDs; use explicit CSV assumptions | Filename rejection tests |
| Duplicate names overwrote observations | Reject duplicate names | CSV and filename validation |
| Invalid temperature ordering and nonfinite numbers were accepted | Validate the Zone data contract | Invalid-input tests |
| Wall average exceeded maximum; material assignment differed | Exclude ambiguous record, preserve raw source | Published provenance and valid sample |
| Annual output assumed 8,760 unchanged hours | Optional labelled scenario, zero hours by default | Scenario scaling/range tests |
| Low relative score was described as well insulated | Remove unsupported insulation conclusions | Revised interface and methodology |

## Test coverage

`tests/test_model.py` verifies the three historical arithmetic examples, area/scenario scaling, exact band endpoints, invalid values, missing columns, duplicate CSV observations, filename validation and CSV round-trip/escaping. `tests/test_app.py` exercises the default dataset, empty filtering, parameter changes, flags, navigation persistence and empty upload states with Streamlit AppTest.

The GitHub Actions workflow runs these tests and creates a release ZIP on push or pull request. Adding the workflow is not evidence of a completed remote CI run.

Local execution on September 22, 2026: **10 tests passed** on Windows with Python 3.12.14, Streamlit 1.64.0, Pandas 3.0.6, Plotly 7.1.0 and Pillow 12.3.0. The native Pandas import initially stalled in the restricted sandbox; an approved execution outside that sandbox completed the full suite. This was an environment issue rather than a demonstrated application defect.

## Limits of verification

The test suite does not establish physical accuracy or field performance. It does not reproduce the historical 9.62% and 75% claims, inspect a professional retrofit design, or demonstrate multi-season measurements. Image upload bytes are verified by Pillow; automatic privacy detection and radiometric extraction are absent. AppTest exercises widgets programmatically and is not a substitute for a timed novice usability experiment.

## Archive and release integrity

All 133 original files were moved without changing their contents, and their SHA-256 hashes were checked against the local manifest. The release builder selects only explicit public files and patterns, excluding `.git`, virtual environments, raw course documents, contact details and videos. No remote publication or Git history rewriting is part of this work.
