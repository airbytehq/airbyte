# Operations

Airbyte [connections](/using-airbyte/core-concepts/sync-modes/) support configuring additional transformations that execute after the sync. Useful applications could be:

- Customized normalization to better fit the requirements of your own business context.
- Business transformations from a technical data representation into a more logical and business oriented data structure. This can facilitate usage by end-users, non-technical operators, and executives looking to generate Business Intelligence dashboards and reports.
- Data Quality, performance optimization, alerting and monitoring, etc.
- Integration with other tools from your data stack \(orchestration, data visualization, etc.\)

## Supported Operations

### dbt transformations

#### - git repository url:

A url to a git repository to \(shallow\) clone the latest dbt project code from.

The project versioned in the repository is expected to:

- be a valid dbt package with a `dbt_project.yml` file at its root.
- have a `dbt_project.yml` with a "profile" name declared as described [here](https://docs.getdbt.com/dbt-cli/configure-your-profile).

When using the dbt CLI, dbt checks your `profiles.yml` file for a profile with the same name. A profile contains all the details required to connect to your data warehouse. This file generally lives outside of your dbt project to avoid sensitive credentials being checked in to version control. Therefore, a `profiles.yml` will be generated according to the configured destination from the Airbyte UI.

Note that if you prefer to use your own `profiles.yml` stored in the git repository or in the Docker image, then you can specify an override with `--profiles-dir=<path-to-my-profiles-yml>` in the dbt CLI arguments.

#### - git repository branch \(optional\):

The name of the branch to use when cloning the git repository. If left empty, git will use the default branch of your repository.

#### - docker image:

A Docker image and tag to run dbt commands from. The Docker image should have `/bin/bash` and `dbt` installed for this operation type to work.

A typical value for this field would be for example: `fishtownanalytics/dbt:1.0.0` from [dbt dockerhub](https://hub.docker.com/r/fishtownanalytics/dbt/tags?page=1&ordering=last_updated).

This field lets you configure the version of dbt that your custom dbt project requires and the loading of additional software and packages necessary for your transformations \(other than your dbt `packages.yml` file\).

#### - dbt cli arguments

This operation type is aimed at running the dbt cli.

A typical value for this field would be "run" and the actual command invoked would as a result be: `dbt run` in the docker container.

One thing to consider is that dbt allows for vast configuration of the run command, for example, allowing you to select a subset of models. You can find the [dbt reference docs](https://docs.getdbt.com/reference/dbt-commands) which describes this set of available commands and options.

## Future Operations

- Docker/Script operations: Execute a generic script in a custom Docker container.
- Webhook operations: Trigger API or hooks from other providers.
- Airflow operations: To use a specialized orchestration tool that lets you schedule and manage more advanced/complex sequences of operations in your sync workflow.

## Going Further

In the meantime, please feel free to react, comment, and share your thoughts/use cases with us. We would be glad to hear your feedback and ideas as they will help shape the next set of features and our roadmap for the future. You can head to our GitHub and participate in the corresponding issue or discussions. Thank you!
