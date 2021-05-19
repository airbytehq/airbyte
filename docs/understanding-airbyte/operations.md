# Sync Operations

As part of the [connections](connections/README.md) settings, it is possible to add optional operations to a sync.

Here is the list and descriptions of possible (and future) operations:

## dbt transformations

#### - git repository url:
A url to a git repository to (shallow) clone the latest dbt project code from.

The project versioned in the repository is expected to:

- be a valid dbt package with a `dbt_project.yml` file at its root.
- the `dbt_project.yml` file should declare some "profile" name as described [here](https://docs.getdbt.com/dbt-cli/configure-your-profile).

When using dbt cli, dbt checks your `profiles.yml` file for a profile with the same name. A profile contains all the details required to connect to your data warehouse. This file generally lives outside of your dbt project to avoid sensitive credentials being check in to version control. Therefore, a `profiles.yml` will be generated according to the configured destination from Airbyte UI.

Note that if you prefer to use your own `profiles.yml` stored in the git repository or in the docker image, then you can specify an override with `--profiles-dir=<path-to-my-profiles-yml>` in the dbt cli arguments.

#### - git repository branch (optional):
The name of the branch to use when cloning the git repository. If left empty, git will use the default branch of your repository.

#### - docker image:
A docker image and tag to run dbt commands from. The docker image should have `/bin/bash` and `dbt` installed for this operation type to work.

A typical value for this field would be for example: `fishtownanalytics/dbt:0.19.1` from [dbt dockerhub](https://hub.docker.com/r/fishtownanalytics/dbt/tags?page=1&ordering=last_updated).

Therefore, this field would let you choose the version of dbt that your custom dbt project requires or if you need to load additional pieces of software and packages necessary for your transformations (other than your dbt `packages.yml` file).

#### - dbt cli arguments
This operation type is aimed at running the dbt cli.

A typical value for this field would be "run" and the actual command invoked would as a result be: `dbt run` in the docker container.

However, dbt allows much more control on what to run, select a subset of models etc. You can find the [dbt reference docs](https://docs.getdbt.com/reference/dbt-commands) describing this set of available commands.

## Docker/Script operations

Coming soon!

## Webhook operations

Coming soon!

## Airflow operations

To schedule and manage more advanced and complicated sequences of operations in your sync workflow, it would be more adequate to switch to a proper orchestration specialized tool such as Airflow.

Coming soon!

## Going further

In the meantime, please make sure to react, comment or share your thoughts and use cases from this point on, we would be glad to hear your feedbacks and ideas as they would help us shape the next features (and the roadmap). You can head to our GitHub and participate in the corresponding issue or discussions. Thank you!
