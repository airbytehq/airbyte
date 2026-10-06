# source-incident-io: contributor notes

## `incident_mode` partition router on `actions` and `follow-ups`

The `/v3/actions` and `/v3/follow_ups` endpoints only return records from `standard` and `retrospective` incidents when `incident_mode` is not set. The deprecated `/v2` endpoints returned records from every incident mode, so a plain `/v3` request drops records (on one internal account: 91 of 224 actions and 22 of 602 follow-ups).

To keep parity with `/v2`, both streams use a `ListPartitionRouter` that sends one request series per documented `incident_mode` value: `standard`, `retrospective`, `test`, `tutorial`, `stream`. Each record belongs to exactly one mode, so the partitions do not overlap.

If incident.io adds a new `incident_mode` value (see the `incident_mode` parameter in https://docs.incident.io/openapi/latest.json), add it to the `values` list of both routers in `manifest.yaml` and to `_MODES` in `unit_tests/test_v3_streams.py`. Otherwise records from incidents in that mode will silently stop syncing.
