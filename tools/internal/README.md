Scripts in this directory are for Airbyte's employees

# `demo.sh`

This script helps maintain Airbyte's demo instance:

```shell
./tools/internal/demo.sh ssh # connects you to the airbyte instance
./tools/internal/demo.sh tunnel # creates a local tunnel so you can access the configurable version of airbyte
```

# `compare_versions.sh`

This script compare records output for two given connector versions

## Usage

```shell
./tools/internal/compare_versions.sh # to run script
```

Config, configured catalog and state files should be saved in `config_files` folder:

config - `/config_files/secrets/config.json`

catalog - `/config_files/configured_catalog.json`

state - `/config_files/state.json` (only if you want start sync with state is required)

- Enter connector name: <conneector-name> [source-twitter]
- Enter first connector version: <first-conneector-version> [0.1.1]
- Enter second connector version: <second-conneector-version> [0.1.2]
- Start sync with state (y/n)? [y/n]  
  Depend on choose sync will be started with state or without.
  State should be present in `/config_files/state.json` to start sync with state.
  After 3 wrong tries process will be finished with 1.

If comparing successful and script didn't find difference you get `Records output equal.`
Otherwise you get difference and `Records output not equal.`
