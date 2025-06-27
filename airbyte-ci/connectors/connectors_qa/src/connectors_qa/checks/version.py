# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import subprocess
from pathlib import Path
from typing import Any, Dict

import semver
import yaml  # type: ignore
from connector_ops.utils import Connector  # type: ignore

from connectors_qa import consts
from connectors_qa.models import Check, CheckCategory, CheckResult


class CheckVersionIncrement(Check):
    """Check that the connector version was incremented if files were modified."""

    category = CheckCategory.VERSION
    name = "Connector Version Increment Check"
    description = "Validates that the connector version was incremented if files were modified."

    # _BYPASS_CHECK_FOR = [
    #     consts.METADATA_FILE_NAME,
    #     "acceptance-test-config.yml",
    #     "README.md",
    #     "bootstrap.md",
    #     ".dockerignore",
    #     "unit_tests",
    #     "integration_tests",
    #     "src/test",
    #     "src/test-integration",
    #     "src/test-performance",
    #     "build.gradle",
    #     "erd",
    #     "build_customization.py",
    # ]

    def _should_run(self) -> bool:
        # Always run
        # TODO: don't run if only files changed are in the bypass list or running in the context of the master branch
        return True

    def _get_master_metadata(self, connector: Connector) -> Dict[str, Any] | None:
        """Get the metadata from the master branch or None if unable to retrieve."""
        cwd = Path.cwd().absolute()
        repo_name = "airbyte-enterprise" if "airbyte-enterprise" in cwd.parts else "airbyte"

        fetch_command = [
            "gh",
            "api",
            f"repos/airbytehq/{repo_name}/contents/airbyte-integrations/connectors/{connector.technical_name}/{consts.METADATA_FILE_NAME}?ref=master",
            "-H",
            "Accept: application/vnd.github.v3.raw",
        ]

        try:
            completed_process = subprocess.run(
                fetch_command,
                text=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # New connectors will not have a metadata file in master
            if completed_process.returncode != 0:
                return None

            return yaml.safe_load(completed_process.stdout)["data"]
        except (subprocess.SubprocessError, FileNotFoundError, yaml.YAMLError, KeyError):
            return None

    def _parse_version_from_metadata(self, metadata: Dict[str, Any]) -> semver.Version:
        return semver.Version.parse(str(metadata["dockerImageTag"]))

    def _get_master_connector_version(self, connector: Connector) -> semver.Version:
        """Get the version from the master branch."""
        master_metadata = self._get_master_metadata(connector)
        if not master_metadata:
            return semver.Version.parse("0.0.0")

        return self._parse_version_from_metadata(master_metadata)

    def _get_current_connector_version(self, connector: Connector) -> semver.Version:
        """Get the current version."""
        return self._parse_version_from_metadata(connector.metadata)

    def _are_both_versions_release_candidates(self, master_version: semver.Version, current_version: semver.Version) -> bool:
        """Check if both versions are release candidates."""
        return bool(
            master_version.prerelease
            and current_version.prerelease
            and "rc" in master_version.prerelease
            and "rc" in current_version.prerelease
        )

    def _have_same_major_minor_patch(self, master_version: semver.Version, current_version: semver.Version) -> bool:
        """Check if both versions have the same major, minor, and patch versions."""
        return (
            master_version.major == current_version.major
            and master_version.minor == current_version.minor
            and master_version.patch == current_version.patch
        )

    def _run(self, connector: Connector) -> CheckResult:
        """Run the version increment check."""
        if connector.metadata and connector.metadata.get("ab_internal", {}).get("requireVersionIncrementsInPullRequests") is False:
            return self.skip(connector, "Connector opts out of version increment checks.")

        try:
            master_version = self._get_master_connector_version(connector)
            current_version = self._get_current_connector_version(connector)

            # Require a version increment
            if current_version <= master_version:
                return self.fail(
                    connector,
                    f"The dockerImageTag in {consts.METADATA_FILE_NAME} was not incremented. "
                    f"Master version is {master_version}, current version is {current_version}",
                )

            if self._are_both_versions_release_candidates(master_version, current_version):
                if not self._have_same_major_minor_patch(master_version, current_version):
                    return self.fail(
                        connector,
                        f"Master and current version are release candidates but they have different major, minor or patch versions. "
                        f"Release candidates should only differ in the prerelease part. Master version is {master_version}, "
                        f"current version is {current_version}",
                    )

            return self.pass_(connector, f"Version was properly incremented from {master_version} to {current_version}.")
        except (subprocess.SubprocessError, ValueError, TypeError) as e:
            return self.fail(connector, str(e))


ENABLED_CHECKS = [CheckVersionIncrement()]
