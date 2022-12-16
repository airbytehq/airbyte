# Python Source CSV Export

This collection of tools is used to run the source and capture it's AirbyteMessages and convert them into CSV files. This is useful if you want to manually inspect this data or load it into a database manually.

To be fast, we make use of parallel processing per-stream and only using command-line tools. This works by the main file (`main.sh`) running the source via python and tee-ing the output of RECORDS to sub-scripts which use `jq` to convert the records into CSV-delimited output, which we finally write to disk.

As we read the connector config files, e.g. `--config secrets/config.json --catalog integration_tests/configured_catalog.json --state secrets/state.json`, you can manually step forward your sync if you need to read and store the input in chunks.

## TODO

- This is currently set up very manually, in that we build bash scripts for each stream and manually populate the header information. This information all already lives in the connector's catalog. We probably could build these bash files on-demand with a python script...
