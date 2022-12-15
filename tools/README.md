# Tools

Contains various tools (usually bash scripts) to improve quality of life or the build system.

## Releasing a new version
```
Trigger the Github Action Release Open Source Airbyte (https://github.com/airbytehq/airbyte/actions/workflows/release-airbyte-os.yml)
# Merge PR created by the Github Action
# The [Create Release github action](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/create-release.yml) should be automatically triggered by this merge, which will automatically create a new release of OSS Airbyte. 
```
