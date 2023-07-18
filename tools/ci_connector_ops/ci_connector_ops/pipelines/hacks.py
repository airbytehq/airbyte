#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module contains hacks used in connectors pipelines. They're gathered here for tech debt visibility."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import yaml
from ci_connector_ops.utils import ConnectorLanguage
from dagger import DaggerError

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorContext
    from dagger import Directory


async def _patch_dockerfile(context: ConnectorContext, connector_dir: Directory) -> Directory:
    """Patch a python connector dockerfile to pin Cython to <3.0 and pyyaml to ~=5.4
    This patching logic should be removed once we discard Dockerfiles for python connectors in favor of fully daggerized connector build.

    Args:
        context (ConnectorContext): The initialized connector context.
        connector_dir (Directory): The directory containing the Dockerfile to patch.
    Returns:
        Directory: The directory containing the patched dockerfile.
    """

    if context.connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
        context.logger.info(f"Connector language {context.connector.language} does not require a patched dockerfile.")
        return connector_dir
    try:
        dockerfile_content = await connector_dir.file("Dockerfile").contents()
    except DaggerError:
        context.logger.warn(f"Could not find Dockerfile in {connector_dir}. Skipping patching.")
        return connector_dir

    context.logger.warn("Patching dockerfile to pin Cython to <3.0 and pyyaml to ~=5.4")
    patched_dockerfile = []
    pinned = False
    for line in dockerfile_content.splitlines():
        # Workaround for https://github.com/yaml/pyyaml/issues/601
        # Cython 3.0 is incompatible with pyyaml ~=5.4, we shall pin Cython to <3.0
        # Pyyaml should release a new patch version that explicitly pins Cython to <3.0
        if "RUN pip install" in line and not pinned:
            patched_dockerfile.append('RUN pip install --prefix=/install "Cython<3.0" "pyyaml~=5.4" --no-build-isolation')
            patched_dockerfile.append('RUN pip install "Cython<3.0" "pyyaml~=5.4" --no-build-isolation')
            pinned = True
        patched_dockerfile.append(line)
    patched_dockerfile = "\n".join(patched_dockerfile)
    return connector_dir.with_new_file("Dockerfile", patched_dockerfile)


LINES_TO_REMOVE_FROM_GRADLE_FILE = [
    # Do not build normalization with Gradle - we build normalization with Dagger in the BuildOrPullNormalization step.
    "project(':airbyte-integrations:bases:base-normalization').airbyteDocker.output",
]


async def _patch_gradle_file(context: ConnectorContext, connector_dir: Directory) -> Directory:
    """Patch the build.gradle file of the connector under test by removing the lines declared in LINES_TO_REMOVE_FROM_GRADLE_FILE.

    Args:
        context (ConnectorContext): The initialized connector context.
        connector_dir (Directory): The directory containing the build.gradle file to patch.
    Returns:
        Directory: The directory containing the patched gradle file.
    """
    if context.connector.language is not ConnectorLanguage.JAVA:
        context.logger.info(f"Connector language {context.connector.language} does not require a patched build.gradle file.")
        return connector_dir

    try:
        gradle_file_content = await connector_dir.file("build.gradle").contents()
    except DaggerError:
        context.logger.warn(f"Could not find build.gradle file in {connector_dir}. Skipping patching.")
        return connector_dir

    context.logger.warn("Patching build.gradle file to remove normalization build.")

    patched_gradle_file = []

    for line in gradle_file_content.splitlines():
        if not any(line_to_remove in line for line_to_remove in LINES_TO_REMOVE_FROM_GRADLE_FILE):
            patched_gradle_file.append(line)
    return connector_dir.with_new_file("build.gradle", "\n".join(patched_gradle_file))


def _patch_cat_config(context: ConnectorContext, connector_dir: Directory) -> Directory:
    """Patch the acceptance-test-config.yml file of the connector under test by replacing the connector image dev tag with the git revision tag."""

    if not context.connector.acceptance_test_config:
        return connector_dir

    context.logger.info("Patching acceptance-test-config.yml to use connector image with git revision tag and not dev.")

    patched_cat_config = deepcopy(context.connector.acceptance_test_config)
    patched_cat_config["connector_image"] = context.connector.acceptance_test_config["connector_image"].replace(
        ":dev", f":{context.git_revision}"
    )
    return connector_dir.with_new_file("acceptance-test-config.yml", yaml.safe_dump(patched_cat_config))


async def patch_connector_dir(context: ConnectorContext, connector_dir: Directory) -> Directory:
    """Patch a connector directory: patch cat config, gradle file and dockerfile.

    Args:
        context (ConnectorContext): The initialized connector context.
        connector_dir (Directory): The directory containing the connector to patch.
    Returns:
        Directory: The directory containing the patched connector.
    """
    patched_connector_dir = await _patch_dockerfile(context, connector_dir)
    patched_connector_dir = await _patch_gradle_file(context, patched_connector_dir)
    patched_connector_dir = _patch_cat_config(context, patched_connector_dir)
    return patched_connector_dir.with_timestamps(1)
