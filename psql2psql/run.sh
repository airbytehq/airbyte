#!/bin/sh
./init_db
./tap-postgres/bin/tap-postgres --config tap_config.json --properties tap_catalog.json | ./singer-target-postgres/bin/target-postgres --config target_config.json >> state.json

