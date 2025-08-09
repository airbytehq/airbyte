# Connectors Insights

Connectors Insights is a Python project designed to generate various insights from analysis of our connectors code. This project utilizes Poetry for dependency management and packaging.

## Artifacts Produced
The project generates the following artifacts:

- `insights.json`: Contains general insights and metadata about the connectors.
- `sbom.json`: Contains the Software Bill Of Material. Produced by [Syft](https://github.com/anchore/syft).

## Installation
To install the project and its dependencies, ensure you have Poetry installed, then run:
```sh
poetry install
```

## Usage
The Connectors Insights project provides a command-line interface (CLI) to generate the artifacts. Below is the command to run the CLI:

```sh
# From airbyte root directory
connectors-insights generate --output-directory <path-to-local-output-dir> --gcs-uri=gs://<bucket>/<key-prefix> --connector-directory airbyte-integrations/connectors/ --concurrency 2 --rewrite
```

### CLI Options

- `generate`: The command to generate the artifacts.

- `-o, --output-dir`: Specifies the local directory where the generated artifacts will be saved. In this example, artifacts are saved to `/Users/augustin/Desktop/insights`.

- `-g, --gcs-uri`: The Google Cloud Storage (GCS) URI prefix where the artifacts will be uploaded. In the form: `gs://<bucket>/<key-prefix>`.

- `-d, --connector-directory`: The directory containing the connectors. This option points to the location of the connectors to be analyzed, here it is `airbyte-integrations/connectors/`.

- `-c, --concurrency`: Sets the level of concurrency for the generation process. In this example, it is set to `2`.

- `--rewrite`: If provided, this flag indicates that existing artifacts should be rewritten if they already exist.

## Example
To generate the artifacts and save them both locally and to GCS, you can use the following command:

```sh
connectors-insights generate --output-directory <path-to-local-output-dir> --gcs-uri=gs://<bucket>/<key-prefix> --connector-directory airbyte-integrations/connectors/ --concurrency 2 --rewrite
```

This command will generate `insights.json` and `sbom.json` files, saving them to the specified local directory and uploading them to the specified GCS URI if `--gcs-uri` is passed.

### Examples of generated artifacts
* [`insights.json`](https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/connector_insights/source-faker/latest/insights.json)
* [`sbom.json`](https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/connector_insights/source-faker/latest/sbom.json)


## Orchestration

This CLI is currently running nightly in GitHub Actions. The workflow can be found in `.github/workflows/connector_insights.yml`.

## Changelog

### 0.3.7
Update Python version requirement from 3.10 to 3.11.

### 0.3.5
Fix permissions issue when installing `pylint` in connector container.

### 0.3.4
Update `dagger` to `0.13.3`.

### 0.3.3
Use SBOM from the connector registry (SPDX format) instead of generating SBOM in the connector insights.

### 0.3.2
Bugfix: Ignore CI on master report if it's not accessible.

### 0.3.1
Skip manifest inferred insights when the connector does not have a `manifest.yaml` file.

### 0.3.0
Adding `manifest_uses_parameters`, `manifest_uses_custom_components`, and `manifest_custom_components_classes` insights.

### 0.2.4
Do not generate insights for `*-scaffold-*` and `*-strict-encrypt` connectors.

### 0.2.3
Share `.docker/config.json` with `syft` to benefit from increased DockerHub rate limit.

### 0.2.2
- Write the sbom output to a file and not to stdout to avoid issues with large outputs.

### 0.2.1
- Implement a high-level error handling to not fail the entire process if a connector fails to generate insights.

### 0.2.0
- Detect deprecated class and module use in connectors.
- Fix missing CDK version for connectors not declaring a CDK name in their metadata.

### 0.1.0
- Initial release
