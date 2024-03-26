# Maintenance through Connector Builder

This document will describe the process through which you can maintain a connector publicly available though our GitHub repository. This process has been split up in five broad steps:
* Build
* Merge into code
* Validation (CATs)
* Release
* Operate/Maintain

The visualization of this process is loosely maintained [here](https://whimsical.com/connector-maintenance-06-23-Rh2xAX5Byw641Xpf7P7qNg@2bsEvpTYSt1Hiz1WXyhZwMwZTwhXRsM2Sv8).

## Build

Goal: Modify the behavior of the connector

Expected output: A manifest.yaml file that represents this new behavior

All the steps mentioned below assume that you have the API available to perform requests. 

### Validate Compatibility of Added Features
Before implementing anything, we need to know if the features you want to add are supported by the Connector Builder. Please refer to the [compatibility guide](./connector-builder-compatibility.md) to confirm if you can build this change within the Connector Builder.

### Config in Connector Builder

Given that the connector already exists and that you want to use the account configured for CATs to iterate during the build phase, you can use [GSM](https://console.cloud.google.com/security/secret-manager?project=dataline-integration-testing) to fetch the existing configuration. Simply write the connector name in the filter bar, click on `SECRET_SOURCE-<name>__CREDS` and under `Actions`, select `View secret value` for the enabled version.

### Importing in Connector Builder

#### Connectors Without Manifest File

This can be either a Python connector or a completely new one. Before implementing it in the Connector Builder, you should confirm if the API is suitable for the connector builder as per the [compatibility guide](./connector-builder-compatibility.md). Once this is confirmed, you are good to go! If not, please reach out to Airbyte to mention the incompatibility reason. This will help us prioritize changes and new features.

#### Connectors With Manifest File
Given a connector with a manifest.yaml file, you can attempt to import it. Go in the Connector Builder, click on "New custom connector" and select "Import a YAML". Given that the import is successful, you should be able to switch to the "UI" tab. Once this is done, there are a couple of manual validations to be performed:
* Were the schemas properly imported? You can validate this by checking the `Declared schema` tab for a specific stream. If not, copy/paste the corresponding schema in the "Declared schema" tab. If the schemas have a "shared" folder, you will need to copy/paste the appropriate file whenever there is a `$ref` key.
* Was the spec properly imported? If the connector has a spec and the Connector Builder does not have any testing value, the spec wasn't properly imported. 

There are a couple of known cases where the import might fail:
* The connector has custom components
    * How to identify: Search for `class_name` in the manifest. 
    * How to fix: Validate if the custom component can be replaced by one from the CDK (see [compatibility guide](./connector-builder-compatibility.md)). If so, replace the custom components by a dummy non-custom component in the manifest.yaml or manually remove the streams that rely on custom components and implement those as if they were new streams
* Nested configurations 
    * How to identify: Search for patterns like `config.<a config key>.<a nested config key>` or `config[<a config key>][<a nested config key>]`
    * How to fix: Flatten the configuration and update the spec. An easy way to do this is to merge both keys like `config.<a config key>_<a nested config key>`

If the import failed for something else, please reach out to the extensibility team with the error so that we can prioritize fixes.

### Implementing the Change
Once the current version of the connector is working in the Connector Builder, you can now implement the change! 

## Merge Into Code

Goal: Make change available in GitHub

Expected output: The updated codebase

Once you can see the behavior change through the Connector Builder, it's time to show this change to everyone. In order to do so, we need to make the updated manifest available to our airbytehq/airbyte repository.

### New Source Setup
If you are working on a new source, we need to initialize the source in our GitHub repository which requires a bit more work than to just update a source. Doing this will require you to use the terminal and Git CLI. To do this:
* If you haven't already done it, pull the git repository using `git clone git@github.com:airbytehq/airbyte.git`. This will create a new folder where the code resides. If you already had the repository on your computer, make sure it's up-to-date by running `git checkout master && git pull`. This command might fail if you have in-flight changes. We recommend committing those changes to a specific branch or stashing them before continuing.
* Go in the root of the repository  
* Run `cd airbyte-integrations/connector-templates/generator && ./generate.sh` and generate a `Configuration Based Source`
* Create a document under `docs/integrations/sources/<name>.md` that describes your source
* Update `airbyte-integrations/connectors/source-<name>/metadata.yml`
    * Set `registries` to reflect where this connector should be available
    * Set `releaseDate`
    * Set `allowedHosts.hosts`. See [Airbyte Connector Acceptance Test suite](../../connector-development/testing-connectors/connector-acceptance-tests-reference.md) for more details
* [Optional] Add an icon at the path matching the metadata.yaml `icon` field

If you intend to continue the process through the GitHub UI, you will have to make those changes available to GitHub by running: `git checkout -b source-<name>-creation && git add . && git commit -m "Creating the new source" && git push --set-upstream origin source-<name>-creation`

### Make the Change Available

#### Through Git CLI
In your local repository:
* Export the manifest from the Connector Builder, remove the `metadata` field and paste everything in `airbyte-integrations/connectors/source-<name>/source_<name>/manifest.yaml`
* If exists, delete the `airbyte-integrations/connectors/source-<name>/source_<name>/schemas` folder
* If exists, delete the `airbyte-integrations/connectors/source-<name>/source_<name>/spec.json` or `airbyte-integrations/connectors/source-<name>/source_<name>/spec.yaml`
* If the connector is low-code with custom components or Python, delete every .py files under `source_<name>` except from `source.py` which should look like
```
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class Source<name>(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

```

Once this is done, commit your changes and push them to GitHub in a branch with a descriptive name.


#### Through GitHub UI
* Go to https://github.com/airbytehq/airbyte/branches, click on "New branch" and enter a descriptive name
* Export the manifest from the Connector Builder, remove the `metadata` field, go to https://github.com/airbytehq/airbyte/tree/<your branch name>/airbyte-integrations/connectors/source-<name>/source_<name>/manifest.yaml, click on the pencil to "Edit this file", paste the Connector Builder manifest and commit this file
* If `https://github.com/airbytehq/airbyte/tree/<your branch name>/airbyte-integrations/connectors/source-<name>/source_<name>/schemas` exists, click on the `...` on the top right side, select `Delete directory` and click on "Commit changes"
* If `https://github.com/airbytehq/airbyte/tree/<your branch name>/airbyte-integrations/connectors/source-<name>/source_<name>/spec.yaml` exists, click on the `...` on the top right side, select `Delete file` and click on "Commit changes"
* Given any file with .py except `source.py` extension under `https://github.com/airbytehq/airbyte/tree/<your branch name>/airbyte-integrations/connectors/source-<name>/source_<name>`, delete the file
* For source.py, ensure that it looks like this:
```
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class Source<name>(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

```

## Validation

Goal: Ensuring the changes work as expected and provide a safety net for the next modifications

Expected output: CATs are green

To ensure we can validate the changes on a connector, CATs are executed. A Connector Acceptance Test is a piece of software that emulates a worker (see architecture [here](../../understanding-airbyte/jobs.md)) and checks the output of commands that the connector is expected to implement. In order to configure these tests, we need to:  
* Create tests scenarios in a sandbox environment: There is no streamlined process to do this. Each product has their own business rules that can't be captured in a unifying document. Given a new connector, this process might require to have pay for a subscription for the product in order to get credentials/workspace/etc... In order to be able to repopulate an API very easily, we suggest the use of a Postman collection or a script.
* Configure what we want to be validated: Using `acceptance-test-config.yml`, you can toggle some of the validations that are performed. The most common cases are:
    * If `expected_records.jsonl` to validate the records that the source returns has been added, ensure `acceptance_tests.basic_read.tests.expect_records` is populated. This might require you to create a catalog for this test suites.
    * If a stream was made incremental, ensure `acceptance_tests.incremental.tests.expect_records` is populated. This might require you to create a catalog for this test suites.
* Set up the configuration: In order to run properly, CATs require a valid config. Those configs often rely on secret. You can use [GSM](https://console.cloud.google.com/security/secret-manager?project=dataline-integration-testing) to modify the existing configuration. Simply write the connector name in the filter bar, click on `SECRET_SOURCE-<name>__CREDS` and `NEW VERSION` and upload the new config.

To execute CATs, there are two options.

### Locally
We recommend using `cd airbyte-integrations/connections/source-<name> && ./acceptance-test-docker.sh` to run them using docker. You might have to change the permissions to run this file. Once it's done, the results will be printed to the terminal.

### In a GitHub pull request
Given that you have pushed you changes on a branch in airbytehq/airbyte, go on https://github.com/airbytehq/airbyte and you should see a yellow banner saying "<branch> had recent pushes less than a minute ago". Click on "Compare & pull request", fill out the template and click on "Create pull request". A check named "Connectors tests / Connectors CI" will run. Once it's done, a new comment will be added to show the test results. 

## Release

Goal: Make the connector available to end-users

Expected output: https://hub.docker.com/r/airbyte/source-<name>/tags shows a recently created tag

The following steps assume that you are getting

* Bump version (Docker file and metadata.yaml) and update changelogs under `docs/integrations`
* Fill the Connector Checklist in the pull request
* If there are breaking changes, follow the process defined by [Connector Breaking Change Release Playbook](https://docs.google.com/document/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit#heading=h.r2xzw0kclodc). A breaking change is a change that requires the user to take action. It can be triggered by a change in the schema, in the config or in the connector behavior. 
* In some specific oauth cases, there are platform changes to be done. <expand on this eventually> 
* Get an approval on the pull request
* Merge

## Operate/Maintain

Goal: Detect issues/bugs and support users

For this, we follow the oncall process already in place. Any comment/feedback should go through the retro process within this initiative. 
