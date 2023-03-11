# Connector Orchestrator
TODO

### Todo
- [ ] sensor on etag
- [ ] write a job to injest the oss catalog and determine which files are in oss and output it to a file
- [ ] write a job to injest the cloud catalog and determine which files are in oss and output it to a file
- [ ] polish sensors and jobs into the appropriate format
- [ ] deal with config
- [ ] write a job that stores past versions of the catalogs by etag
- [ ] write a job that compares the new file with the previous cursor and outputs the diff
- [ ] write a job that uses the cloud and oss catalogs to construct metadata files
- [ ] write a job that replicates metadata files from prod to dev manually


### Notes
what to discuss in readme
- the use of the env file
- local vs cloud development
- the development bucket vs the production bucket
- dagster dev vs dagit
possible ways to build this
https://github.com/slopp/dagster-dynamic-partitions/blob/cf312590bb3a2d95caee670433f00a7f20ddb50c/build/lib/dagster_project/definitions.py
https://github.com/mitodl/ol-data-platform/blob/59b785ab6bd5d73a05d598c9b39bfc8fa4eec65c/src/ol_orchestrate/repositories/edx_gcs_courses.py
https://github.com/dagster-io/dagster/tree/c607767076da21de66ac364f1501c4ed49c20b49/examples/project_fully_featured
https://github.com/DataBiosphere/hca-ingest/blob/61601a7830e224ac5f30c13bf0d605768f97d418/orchestration/hca_orchestration/repositories/common.py

good way to restructure this
https://www.youtube.com/watch?v=ZmUjf3gL1VU
