## What is `airbyte-ci`?

`airbyte-ci` is a CLI written as a python package which is made to execute CI operations on the `airbyte` repo. It is heavily using the [Dagger](https://dagger.cloud/) library to build and orchestrate Docker containers programatically. It enables a centralized and programmatic approach at executing CI logics which can seamlessly run both locally and in remote CI environments.

You can read more why we are using Dagger and the benefit it has provided in this [blog post](https://dagger.io/blog/airbyte-use-case)

## When is a contribution to `airbyte-ci` a good fit for your use case?

- When you want to make global changes to connectors artifacts and build logic.
- When you want to execute something made to run both in CI or for local development. As airbyte-ci logic relies on container orchestration you can have reproducible environment and execution both locally and in a remote CI environment.
- When you want to orchestrate the tests and release of an internal package in CI.

## Who can I ask help from?

The tool has been maintained by multiple Airbyters.
Our top contributors who can help you figuring the best approach to implement your use case are:

- [@alafanechere](https://github.com/alafanechere).
- [@postamar](https://github.com/postamar)
- [@erohmensing](https://github.com/erohmensing)
- [@bnchrch](https://github.com/bnchrch)
- [@stephane-airbyte](https://github.com/stephane-airbyte)

## Where is the code?

The code is currently available in the `airbytehq/airbyte` repo under [ `airbyte-ci/connectors/pipelines` ](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines)

## What use cases it currently supports

According to your need you might want to introduce a new logic to an existing flow or create a new one.
Here are the currently supported use cases. Feel free to grab them as example if you want to craft a new flow, or modify an existing one. If you are not sure about which direction to take feel free to ask advices (see [*Who Can I ask help?*](## Who can I ask help from?) from section).

| Command group                                                                                                                                     | Feature                                                  | Command                                       | Entrypoint path                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Running test suites connectors                           | `airbyte-ci connectors test`                  | [`airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/commands.py)                         |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Building connectors                                      | `airbyte-ci connectors build`                 | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/build_image/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/build_image/commands.py)                     |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Publishing connectors                                    | `airbyte-ci connectors publish`               | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/publish/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/publish/commands.py)                             |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Bumping connectors versions                              | `airbyte-ci connectors bump_version`          | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/bump_version/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/bump_version/commands.py)                   |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Listing connectors                                       | `airbyte-ci connectors list`                  | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/list/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/list/commands.py)                                   |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Migrate a connector to use our base image                | `airbyte-ci connectors migrate_to_base_image` | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/migrate_to_base_image/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/migrate_to_base_image/commands.py) |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Migrate a connector to use `poetry` as a package manager | `airbyte-ci connectors migrate_to_poetry`     | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/migrate_to_poetry/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/migrate_to_poetry/commands.py)         |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Upgrade the base image used by a connector               | `airbyte-ci connectors upgrade_base_image`    | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/upgrade_base_image/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/upgrade_base_image/commands.py)       |
| [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) | Upgrade the CDK version used by a connector              | `airbyte-ci connectors upgrade_cdk`           | [`airbyte-ci/connectors/pipelines/airbyte_ci/connectors/upgrade_cdk/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/upgrade_cdk/commands.py)                     |
| [`format`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/format/commands.py#L32)          | Check that the full repo is correctly formatted          | `airbyte-ci format check all`                 | [`airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/format/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/format/commands.py#L78)                                       |
| [`format`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/format/commands.py#L32)          | Format the whole repo                                    | `airbyte-ci format fix all`                   | [`airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/format/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/format/commands.py#L101)                                      |
| [`test`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/test/commands.py#L107)             | Run tests on internal poetry packages                    | `airbyte-ci test`                             | [`airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/test/commands.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/test/commands.py#L107)                                          |
| [`poetry`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/poetry/commands.py#L33)          | Publish a poetry package to PyPi                         | `airbyte-ci poetry publish`                   | [`airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/poetry/publish/commands.py`](https:github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/poetry/publish/commands.py#L69)                         |

## How to install the package for development

There are multiple way to have dev install of the tool. Feel free to grab the one you prefer / which works for you.
**Please note that all the install mode lead to an editable install. There's no need to re-install the tool following a code change**.

### System requirements

- `Python` > 3.10
- [`Poetry`](https://python-poetry.org/) or [`pipx`](https://github.com/pypa/pipx)

### Installation options

There are many ways to install Python tools / packages.

For most users we recommend you use `make` but `pipx` and `poetry` are also viable options

#### With `make`

```bash
 # From airbyte repo root:
 make tools.airbyte-ci-dev.install
```

#### With `pipx`

```bash
# From airbyte-ci/connectors/pipelines:
pipx install --editable --force .
```

#### With `poetry`

⚠️ This places you in a python environment specific to airbyte-ci. This can be a problem if you are developing airbyte-ci and testing/using your changes in another python project.

```bash
# From airbyte-ci/connectors/pipelines
poetry install
poetry shell
```

## Main libraries used in the tool

### [Click](https://click.palletsprojects.com/en/8.1.x/)

This is a python light CLI framework we use to declare entrypoint. You'll interact with it if you have to deal with commands, command groups, option, arguments etc.

### [Dagger](https://dagger-io.readthedocs.io/en/sdk-python-v0.15.3/)

This is an SDK to build, execute and interact with Docker containers in Python. It's basically a nice API on top of [BuildKit](https://docs.docker.com/build/buildkit/). We use containers to wrap the majority of `airbyte-ci` operations as it allows us to:

- Execute language agnostic operations: you can execute bash commands, gradle tasks, etc. in containers with Python. Pure magic!
- Benefit from caching by default. You can consider a Dagger operation a "line in a Dockerfile". Each operation is cached by BuildKit if the inputs of the operation did not change.
- As Dagger exposes async APIs we can easily implement concurrent logic. This is great for performance.

**Please note that we are currently using v0.15.3 of Dagger. The library is under active development so please refer to [this specific version documentation](https://dagger-io.readthedocs.io/en/sdk-python-v0.15.3/) if you want an accurate view of the available APIs.**

### [anyio](https://anyio.readthedocs.io/en/stable/basics.html) / [asyncer](https://asyncer.tiangolo.com/)

As Dagger exposes async APIs we use `anyio` (and the `asyncer` wrapper sometimes) to benefit from [structured concurrency](https://en.wikipedia.org/wiki/Structured_concurrency).
**Reading the docs of these libraries is a must if you want to declare concurrent logics.**

## Design principles

_The principles set out below are ideals, but the first iterations on the project did not always respect them. Don't be surprised if you see code that contradicts what we're about to say (tech debt...)._

### `airbyte-ci` is _just_ an orchestrator

Ideally the steps declared in airbyte-ci pipeline do not contain any business logic themselves. They call external projects, within containers, which contains the business logic.

Following this principles will help in decoupling airbyte-ci from other project and make it agnostic from business logics that can quickly evolve. Not introducing business logic to the tool encourages abstraction efforts that can lead to future leverage.

Maintaining business logic in smaller projects also increases velocity, as introducing a new logic would not require changing airbyte-ci and, which is already a big project in terms of code lines.

#### Good examples of this principle

- `connectors-qa`: We want to run specific static checks on all our connectors: we introduced a specific python package ([`connectors-qa`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/connectors_qa/README.md#L1))which declares and run the checks on connectors. We orchestrate the run of this package inside the [QaChecks](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/steps/common.py#L122) step. This class is just aware of the tool location, its entry point, and what has to be mounted to the container for the command to run.
- Internal package testing: We expose an `airbyte-ci test` command which can run a CI pipeline on an internal poetry package. The pipeline logic is declared at the package level with `poe` tasks in the package `pyproject.toml`. `airbyte-ci` is made aware about what is has to run by parsing the content of the `[tool.airbyte_ci]` section of the `pyproject.toml`file. [Example](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/pyproject.toml#L39)

### No command or pipeline should be language specific

We oftentimes have to introduce new flows for connectors / CDK. Even if the need for this flow is currently only existing for a specific connector language (Python / Java), we should build language agnostic command and pipelines. The language specific implementation should come at the most downstream level of the pipeline and we should leverage factory like patterns to get language agnostic pipelines.

#### Good example of this principle: our build command

The `airbyte-ci connectors build` command can build multiple connectors of different languages in a single execution.
The higher level [`run_connector_build_pipeline` function](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/build_image/steps/__init__.py#L36) is connector language agnostic and calls connector language specific sub pipelines according to the connector language.
We have per-language submodules in which language specific `BuildConnectorImages` classes are implemented:

- [`python_connectors.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/build_image/steps/python_connectors.py)
- [`java_connectors.py`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/build_image/steps/java_connectors.py#L14)

### Pipelines are functions, steps are classes

A pipeline is a function:

- instantiating and running steps
- collecting step results and acting according to step results
- returning a report

A step is a class which inheriting from the `Step` base class:

- Can be instantiated with parameters
- Has a `_run` method which:
  - Performs one or multiple operations according to input parameter and context values
  - Returns a `StepResult` which can have a `succeeded`, `failed` or `skipped` `StepStatus`

**Steps should ideally not call other steps and the DAG of steps can be understand by reading the pipeline function.**

#### Step examples:

- [`PytestStep`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/steps/python_connectors.py#L29)
- [`GradleTask`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/steps/gradle.py#L21)

#### Pipelines examples:

- [`run_connector_publish_pipeline`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/publish/pipeline.py#L296)
- [`run_connector_test_pipeline`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/pipeline.py#L48)

## Main classes

### [`PipelineContext`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/models/contexts/pipeline_context.py#L33) (and [`ConnectorContext`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/context.py#L33), [`PublishConnectorContext`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/publish/context.py#L19))

Pipeline contexts are instantiated on each command execution and produced according to the CLI inputs. We populate this class with global configuration, helpers and attributes that are accessed during pipeline and step execution.

It has, for instance, the following attributes:

- The dagger client
- The list of modified files on the branch
- A `connector` attribute
- A `get_connector_dir` method to interact with the connector
- Global secrets to connect to protected resources
- A `is_ci` attribute to know if the current execution is a local or CI one.

We use `PipelineContext` with context managers so that we can easily handle setup and teardown logic of context (like producing a `Report`)

### [`Step`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/models/steps.py#L189)

`Step` is an abstract class. It is meant to be inherited for implementation of pipeline steps which are use case specific. `Step` exposes a public `run` method which calls a private `_run` method wrapped with progress logger and a retry mechanism.

When declaring a `Step` child class you are expected to:

- declare a `title` attribute or `property`
- implement the `_run` method which should return a `StepResult` object. You are free to override the `Step` methods if needed.

### [`Result` / `StepResult`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/models/steps.py#L86)

The `Result` class (and its subclasses) are meant to characterize the result of a `Step` execution.
`Result` objects are build with:

- `StepStatus` (success/failure/skipped)
- `stderr`: The standard error of the operation execution
- `stdout` : The standard output of the operation execution
- `excinfo`: An Exception instance if you want to handle an operation error
- `output`: Any object you'd like to attach to the result for reuse in other Steps
- `artifacts`: Any object produced by the Step that you'd like to attach to the `Report`

### [`Report`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/models/reports.py#L34)

A `Report` object is instantiated on `PipelineContext` teardown with a collection of step results. It is meant to persists execution results as json / html locally and in remote storage to share them with users or other automated processes.

## Github Action orchestration

A benefit of declaring CI logic in a centralized python package is that our CI logic can be agnostic from the CI platform it runs on. We are currently using GitHub actions. This section will explain how we run `airbyte-ci` in GitHub actions.

### Multiple workflows re-using the same actions

Each CI use case has its own Github Action worfklow:

- [Connector testing](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/connectors_tests.yml#L1)
- [Connector publish](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/publish_connectors.yml#L1)
- [Internal package testing](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/airbyte-ci-tests.yml#L1)
- etc.

They all use the [`run-airbyte-ci` re-usable action](https://github.com/airbytehq/airbyte/blob/master/.github/actions/run-airbyte-ci/action.yml#L1)to which they provide the `airbyte-ci` command the workflow should run and other environment specific options.

The `run-airbyte-ci` action does the following:

- [Pull Dagger image and install airbyte-ci from binary (or sources if the tool was changed on the branch)](https://github.com/airbytehq/airbyte/blob/master/.github/actions/run-airbyte-ci/action.yml#L105)
- [Run the airbyte-ci command passed as an input with other options also passed as inputs](https://github.com/airbytehq/airbyte/blob/main/.github/actions/run-airbyte-ci/action.yml#L111)

## A full example: breaking down the execution flow of a connector test pipeline

Let's describe and follow what happens when we run:
`airbyte-ci connectors --modified test`

**This command is meant to run tests on connectors that were modified on the branch.**
Let's assume I modified the `source-faker` connector.

### 1. The `airbyte-ci` command group

On command execution the [`airbyte-ci` command group](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/cli/airbyte_ci.py#L186) acts as the main entrypoint. It is:

- Provisioning the click context object with options values, that can be accessed in downstream commands.
- Checking if the local docker configuration is correct
- Wrapping the command execution with `dagger run` to get their nice terminal UI (unless `--disable-dagger-run` is passed)

### 2. The `connectors` command subgroup

After passing through the top level command group, click dispatches the command execution to the [`connectors`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/commands.py#L237) command subgroup.
It continues to populate the click context with other connectors specific options values which will be consumed by the final `test` command.
**It also computes the list of modified files on the branch and attach this list to the click context.** The `get_modified_files` function basically performs a `git diff` between the current branch and the `--diffed-branch` .

### 3. Reaching the `test` command

After going through the command groups we finally reach the actual command the user wants to execute: the [`test` command](https://github.com/airbytehq/airbyte/blob/main/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/commands.py#L72).

This function:

- Sends a pending commit status check to Github when we are running in CI
- Determines which steps should be skipped or kept according to user inputs (by building a `RunStepOptions` object)
- Instantiate one `ConnectorContext` per connector under test: we only modified `source-faker` so we'll have a single `ConnectorContext` to work with.
- Call `run_connectors_pipelines` with the `ConnectorContext`s and

#### 4. Globally dispatching pipeline logic in `run_connectors_pipeline`

[`run_connectors_pipeline`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/pipeline.py#L83) gets called with all the `ConnectorContext` produced according to the user inputs and a callable which captures the pipeline logic: `run_connector_test_pipeline`.
`run_connectors_pipeline`, as its taking a pipeline callable, it has no specific pipeline logic.

This function:

- Instantiates the dagger client
- Create a task group to concurrently run the pipeline callable: we'd concurrently run test pipeline on multiple connectors if multiple connectors were modified.
- The concurrency of the pipeline is control via a semaphore object.

#### 5. Actually running the pipeline in [`run_connector_test_pipeline`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/pipeline.py#L48)

_Reminder: this function is called for each connector selected for testing. It takes a `ConnectorContext` and a `Semaphore` as inputs._

The specific steps to run in the pipeline for a connector is determined by the output of the [`get_test_steps`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/pipeline.py#L32) function which is building a step tree according to the connector language.

**You can for instance check the declared step tree for python connectors [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/test/steps/python_connectors.py#L249).**:

```python
def get_test_steps(context: ConnectorContext) -> STEP_TREE:
    """
    Get all the tests steps for a Python connector.
    """
    return [
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UNIT,
                step=UnitTests(context),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            )
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.INTEGRATION,
                step=IntegrationTests(context),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.PYTHON_CLI_VALIDATION,
                step=PyAirbyteValidation(context),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
                step=AcceptanceTests(context, context.concurrent_cat),
                args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
        ],
    ]
```

After creating the step tree (a.k.a a _DAG_) it enters the `Semaphore` and `PipelineContext` context manager to execute the steps to run with `run_steps`. `run_steps` executes steps concurrently according to their dependencies.

Once the steps are executed we get step results. We can build a `ConnectorReport` from these results. The report is finally attached to the `context` so that it gets persisted on `context` teardown.

```python
async def run_connector_test_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """
    Compute the steps to run for a connector test pipeline.
    """
    all_steps_to_run: STEP_TREE = []

    all_steps_to_run += get_test_steps(context)

    if not context.code_tests_only:
        static_analysis_steps_to_run = [
            [
                StepToRun(id=CONNECTOR_TEST_STEP_ID.VERSION_INC_CHECK, step=VersionIncrementCheck(context)),
                StepToRun(id=CONNECTOR_TEST_STEP_ID.QA_CHECKS, step=QaChecks(context)),
            ]
        ]
        all_steps_to_run += static_analysis_steps_to_run

    async with semaphore:
        async with context:
            result_dict = await run_steps(
                runnables=all_steps_to_run,
                options=context.run_step_options,
            )

            results = list(result_dict.values())
            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report

        return report
```

#### 6. `ConnectorContext` teardown

Once the context manager is exited (when we exit the `async with context` block) the [`ConnectorContext.__aexit__` function is executed](https://github.com/airbytehq/airbyte/blob/main/airbyte-ci/connectors/pipelines/pipelines/airbyte_ci/connectors/context.py#L237)

This function:

- Determines the global success or failure state of the pipeline according to the StepResults
- Uploads connector secrets back to GSM if they got updated
- Persists the report to disk
- Prints the report to the console
- Uploads the report to remote storage if we're in CI
- Updates the per connector commit status check
