# Google Sheets Source 

This is the repository for the Google Sheets source connector, written in Python. 
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/sources/googlesheets). 

## Local development
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:source-google-sheets:build
```

This should generate a virtualenv for this module in `source-google-sheets/.venv`. Make sure this venv is active in your 
development env of choice. If you are on the terminal, run the following from this directory: 
```
source .venv/bin/activate
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv. 

**All the instructions below assume you have correctly activated the virtualenv.**. 

To run unit tests locally, from the connector root run:
```
python setup.py test
``` 

To run integration tests: 
1. Configure credentials as appropriate, described below
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-google-sheets:integrationTest`

## Configure credentials
### Configuring credentials as a community contributor
Follow the instructions in the documentation above for generating credentials to access the Google API, then put those 
in a file named `secrets/credentials.json`. 

### Airbyte Employee
Credentials are available in RPass under the secret name `google sheets integration test creds`.
