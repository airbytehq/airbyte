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

### 0.1.0
- Initial release
