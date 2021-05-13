# CDK Speedrun (Any% Route)

## Dependencies

1. Python &gt;= 3.7
2. Docker
3. NodeJS

## Generate the Template

```bash
$ cd airbyte-integrations/connector-templates/generator # start from repo root
$ npm install
$ npm run generate
```

Select the `Python HTTP API Source` and name it `python-http-example`.

```text
cd ../../connectors/source-<name>
python -m venv .venv # Create a virtual environment in the .venv directory
source .venv/bin/activate # enable the venv
pip install -r requirements.txt
```