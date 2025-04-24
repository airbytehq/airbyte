# Developing Connectors Locally

This document outlines the steps to develop a connector locally using the `local-connector-development` script.

When developing connectors locally, you'll want to install the following tools locally:

1. [**Poe the Poet**](#poe-the-poet) - Used as a common task interface for defining and running development tasks.
1. [`docker`](#docker) - Used when building and running connector container images.
1. [`airbyte-ci`](#airbyte-ci) - Used for a large number of tasks such as building and publishing.
1. [`gradle`](#gradle) - Useful when working on Java and Kotlin connectors.

## Poe the Poet

Poe the Poet - This tool allows you to perform common connector tasks from a single entrypoint.

To see a list of available tasks, run `poe` from any directory in the `airbyte` repo.

Notes:

1. When running `poe` from the root of the repo, you'll have the options `connector`, `source`, and `destination`. These will each pass the tasks you request along to the specified connector's directory.
2. When running `poe` from a connector directory, you'll get a specific list of available tasks, like `lint`, `check-all`, etc. The available commands may vary by connector and connector type (java vs python vs manifest-only), so run `poe` on its own to see what commands are available.
3. Poe tasks are there to help you, but they are _not_ the only way to run a task. Please feel encouraged to review, copy, paste, or combing steps from the task definitions in the `poe_tasks` directory. And if you find task invocation patterns that are especially helpful, please consider contributing back to those task definition files by creating a new PR.

## Docker

We recommend Docker Desktop but other container runtimes might be available. A full discussion of how to install and use docker is outside the scope of this guide.

See [Debugging Docker](./debugging-docker.md) for common tips and tricks.

## airbyte-ci

Airbyte CI `(airbyte-ci`) is a Dagger-based tool for accomplishing specific tasks. See `airbyte-ci --help` for a list of commands you can run.

## Gradle

Gradle is used in Java and Kotlin development.  A full discussion of how to install and use docker is outside the scope of this guide. Similar to running `poe`, you can run `gradle tasks` to view a list of available Gradle development tasks.
