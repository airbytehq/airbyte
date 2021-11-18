# Tools

## Releasing a new version
```
Trigger the Github Action Release Open Source Airbyte (https://github.com/airbytehq/airbyte/actions/workflows/release-airbyte-os.yml)
# Merge PR created by the Github Action
git checkout master
git pull --no-rebase
./tools/bin/tag_version.sh
```
