# Airbyte-Enterprise

This is the closed-source equivalent to https://github.com/airbytehq/airbyte

## Setup

This repo has `airbytehq/airbyte` as a submodule, located in `airbyte-submodule`, and then a lot of symlinks so various tools like airbyte-ci work.
The first time that you clone this repo, you need to setup the submodule: `git submodule init && git submodule update --remote`.
