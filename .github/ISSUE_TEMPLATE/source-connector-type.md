---

name: Source Connector Type
about: Add a new type or update an existing type in source connector
title: '[EPIC] Add new type / update <type-name> in source connector <connector-name>'
labels: area/connectors, needs-triage
assignees: ''

---
  
## Summary
(Choose one of the two below.)
- [ ] Support new type <type-name>
- [ ] Update existing type <type-name>

## TODOs
(Complete the TODOs based on the instruction, and convert each bullet point with the `[Issue]` tag into an issue.)
- [ ] [Issue] Add a new destination acceptance test (DAT) test case for this type.
- List every destination below, either update the destination to suppor this type, or override its DAT to bypass the new test case.
  - [ ] Example: [Issue] support <type-name> in destination bigquery
- [ ] [Issue] Make sure every destination can pass the new DAT test case.
  - Even if a destination does not need to support this type, its DAT should not break.
- List every source that should support this type below.
  - [ ] Example: [Issue] support <type-name> in source github

## Desired Timeline
