# POC of CI connector pipelines in python

This Python subpackage of `ci-connector-ops` gathers the POC code we're working on to:
- Rewrite [airbyte-python.gradle](https://github.com/airbytehq/airbyte/blob/7d7e48b2a342a328fa74c6fd11a9268e1dcdcd64/buildSrc/src/main/groovy/airbyte-python.gradle) and [airbyte-connector-acceptance-test.gradle](https://github.com/airbytehq/airbyte/blob/master/buildSrc/src/main/groovy/airbyte-connector-acceptance-test.gradle) in Python.
- Centralize the CI logic for connector testing 
- Try out Dagger.io as a promising tool that can provide parallelism and caching out of the box for CI 

## Install and use
From `airbyte` repo root:

### Install
```bash
cd tools/ci_connector_ops
python -m venv .venv (please use at least Python 3.10)
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
cd ../..
```

### Use

### [Optional] Set your environment variables
Optional: Set the DIFFED_BRANCH env variable. 
This should be the branch name you want the internal git diff to run on to spot connector changes.
```bash
export DIFFED_BRANCH=master #This is already the default
```

Optional: Set your `GCP_GSM_CREDENTIALS` env variable. **If you don't set it you won't be able to run acceptance tests on connectors that uses secrets from GSM.** 
More details [here](https://github.com/airbytehq/airbyte/blob/master/tools/ci_credentials/README.md#L20).

```bash
export GCP_GSM_CREDENTIALS=`cat <path to service account json file>`
```


### **Run the pipelines for a specific connectors**
(source-pokeapi does not require GSM access)
```bash
connectors-ci test-connectors source-pokeapi
```

### **Run the pipeline for multiple connectors**

```bash
connectors-ci test-connectors source-pokeapi source-openweather
```

### **Run the pipeline for the connectors you changed on the branch**

```bash
touch airbyte-integrations/connectors/source-pokeapi/random_file_addition.txt
connectors-ci test-all-modified-connectors #the source-pokeapi pipeline should run
```



## What does a connector pipeline run

```mermaid
flowchart LR;
    AB_GIT_REPO[Airbyte Git Repo] --> MOUNT_AB[Mount Airbyte repo to container];
    AB_GIT_REPO[Airbyte Git Repo] --> MOUNT_CONN[Mount connector source code to container];
    DOWN_SECRETS[Download secrets from GSM]-->CAT
    MOUNT_AB-->QA[Run QA checks];
    MOUNT_CONN-->FORMAT[Code format checks];
    MOUNT_CONN-->INSTALL_CONN[Install connector package in container];
    INSTALL_CONN-->UNIT_TESTS[Run unit tests];
    UNIT_TESTS-->INTEGRATION_TESTS[Run integration tests];
    UNIT_TESTS-->DOCKER_BUILD[Docker build connector dev image];
    DOCKER_BUILD-->CAT[Run acceptance tests];
    CAT-->UPLOAD_SECRETS[Upload updated secrets to GSM];
    CAT-->REPORT[Build test report];
    UNIT_TESTS-->REPORT;
    INTEGRATION_TESTS-->REPORT;
    QA-->REPORT;
    FORMAT-->REPORT;
    REPORT--if in CI-->UPLOAD[Upload to S3];
```

This is the DAG we expect for every connector for which the pipeline is triggered.
The Airbyte git repo will be the local one if you use `--is-local=True` command line option.
The connector secrets won't be downloaded nor uploaded if you use the `--use-remote-secrets=False` command line option.

## Questions for the Dagger team (in priority order)

Dear Dagger team. You should be able to execute the code we pushed with the instructions above.
Please ignore the `Set your environment variables` step and focus on running `connectors-ci test-connectors source-pokeapi` to reproduce the problems I mention below.

1. ~~How to handle exit codes: if exit_code != 0 an exception is thrown and stops the other pipeline execution. Code context [here](https://github.com/airbytehq/airbyte/blob/7d7e48b2a342a328fa74c6fd11a9268e1dcdcd64/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/tests.py#L25)~~ A stop-gap solution was implemented waiting for this [issue](https://github.com/dagger/dagger/issues/3192) to be fixed.
2. Can we make with_mounted_directory writable so that the container can write to the host FS? Code context [here](https://github.com/airbytehq/airbyte/blob/7d7e48b2a342a328fa74c6fd11a9268e1dcdcd64/tools/ci_connector_ops/ci_connector_ops/pipelines/actions/tests.py#L119)
Dagger team answer: We'll implement a flag to run privileged `with_exec` that will allow containers to write on the host FS.
3. How to get access to visualizations: We'd love to have dynamic status checks on our GitHub PRs, with links to pipeline visualization [like](https://propeller.fly.dev/runs/da68273e-48d8-4354-8d8b-efaccf2792b9).
Dagger team answer: coming soon. 
4. Can we build and tag an image in Dagger?
Dagger team answer: Run a local docker registry and publish images to this directory during the pipeline execution.
5. What are the best practices to report success failure details?
6. What are the best practices to write tests for pipelines?
Dagger team answer: Get inspirations from their own repo [here](https://github.com/dagger/dagger/tree/main/sdk/python/tests). 
7. What would be your suggestion to run `docker scan` from dagger to spot vulnerabilities on our connectors?
Dagger team answer: A scanning tool should be wrapped in a container to scan images from Dagger.
8. Do you have a tool to re-order logs line by order of pipeline after execution?
A log grouping tool is under construction: https://www.youtube.com/watch&ab_channel=Dagger

### Airbyte specific context that could help you understand our workflow.
- We always use a :dev tag to tag images of connector we build locally. We try to never publish these images to a public repository.
- We run a container called connector-acceptance-test which is a global test suite for all our connectors. This test suite is ran against a connector under test container, (usually using its :dev image).
- Connector-acceptance-test is a customizable test suite (built with pytest) configured with per-connector `acceptance-test-config.yml` files ([e.g.](https://github.com/airbytehq/airbyte/blob/b0c5f14db6a905899d0f9c043954abcc5ec296f0/airbyte-integrations/connectors/source-pokeapi/acceptance-test-config.yml#L1))
- As connector-acceptance-test is running connector containers, it triggers actual HTTP requests the public API of our source/destination connector. This is why we need to load secrets configuration with our test account credentials to these connector containers. connector-acceptance-test is also generating dynamic connector configurations to check the behavior of a connector under test when it is  it different structure of configuration files. 