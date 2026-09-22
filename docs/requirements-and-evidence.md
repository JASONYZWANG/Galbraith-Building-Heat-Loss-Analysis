# Requirements and implementation evidence

Status applies to the curated release. A design target is not a test result.

| Requirement or goal | Evidence / implementation | Status |
|---|---|---|
| Identify potential heat-loss zones | Manual thermal survey and labelled observations | Demonstrated manually; no automatic detection |
| Quantify severity | `model.analyze`, fixed bands, example calculations | Implemented as a proxy; not calibrated heat flow |
| Organize and display results | Chart, table, filters, sorting, CSV | Implemented |
| At least three severity levels | Low, Medium, High function and boundary tests | Implemented |
| Repeat measurement variation below 10% | Presentation reports 9.62%; incomplete calculation trail | Historical claim, not independently verified |
| First-time room scan within 25 minutes | PR target; no retained timed novice experiment | Unverified |
| Interpret results within 5 minutes | PR target; later CDS also mentions 45 seconds | Unverified; source targets differ |
| Transfer to another building | Portable workflow by design | Not field-demonstrated in a second building |
| Cost at or below CAD 200 | PR/CDS constraint | No complete retained bill of materials or spend verification |
| Heating and shoulder-season operation | Variable reference input | Configurable; seasonal performance unverified |
| Privacy in images | Original design proposed filtering/blurring | No automated anonymization in code |
| Persistent timestamps and location tags | Proposed CDS architecture | Not implemented in release |
| Digital floor-plan heat map | Concept illustrations | Not implemented in release |
| Automatic radiometric reading | Intended camera-to-data workflow | Not implemented; manual transcription |
| Reproducible software workflow | Included sample, pinned dependencies and tests | Implemented; see verification record |

## Acceptance evidence in this repository

The sample must reproduce 66.12, 32.49 and 17.08 W/m² for the three published zones. Editing an area must scale W without changing W/m² or its band. Editing U must update the table and detail consistently. Invalid temperatures, nonfinite numbers, missing columns and duplicate names must be rejected. Export must retain reference assumptions and all observations even if the display is filtered.

These acceptance checks address software behavior. Broader physical and user-performance requirements remain open and are listed as future work rather than marked complete.
