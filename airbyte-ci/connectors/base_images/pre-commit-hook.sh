#!/bin/bash

set -o errexit

export GIT_HOOK="true"
base_images_project_file_path="airbyte-ci/connectors/base_images/"

set -o xtrace
poetry install -C $base_images_project_file_path
# This will generate the changelog and dockerfiles
poetry run -C $base_images_project_file_path build
python_base_image_changelog="CHANGELOG_PYTHON_CONNECTOR_BASE_IMAGE.md"
generated_directory="generated"
lockfile="poetry.lock"
git add "${base_images_project_file_path}${python_base_image_changelog}"
git add "${base_images_project_file_path}${generated_directory}"
git add "${base_images_project_file_path}${lockfile}"
unset GIT_HOOK
