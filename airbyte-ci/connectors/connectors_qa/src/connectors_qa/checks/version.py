# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

import requests  # type: ignore
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
        # TODO: test out if this works on the private airbyte-enterprise repo - consider using git-based approach
        github_url_prefix = "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors"
        master_metadata_url = f"{github_url_prefix}/{connector.technical_name}/{consts.METADATA_FILE_NAME}"
        response = requests.get(master_metadata_url)

        # New connectors will not have a metadata file in master
        if not response.ok:
            return None
        return yaml.safe_load(response.text)["data"]

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
        except (requests.HTTPError, ValueError, TypeError) as e:
            return self.fail(connector, str(e))


ENABLED_CHECKS = [CheckVersionIncrement()]
