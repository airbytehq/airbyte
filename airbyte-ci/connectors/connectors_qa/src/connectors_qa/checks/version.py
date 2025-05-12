

import requests
import semver
import yaml
from typing import Optional, Dict, Any

from connector_ops.utils import Connector  # type: ignore

from connectors_qa.models import Check, CheckCategory, CheckResult


METADATA_FILE_NAME = "metadata.yaml"
GITHUB_URL_PREFIX_FOR_CONNECTORS = "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors"


class VersionCheck(Check):
    """Base class for version-related checks."""
    
    @property
    def category(self) -> CheckCategory:
        return CheckCategory.METADATA
    
    @property
    def name(self) -> str:
        return "Version Check"
    
    @property
    def description(self) -> str:
        return "Validates the connector version."
    
    def _get_github_master_metadata_url(self, connector: Connector) -> str:
        return f"{GITHUB_URL_PREFIX_FOR_CONNECTORS}/{connector.technical_name}/{METADATA_FILE_NAME}"
    
    def _get_master_metadata(self, connector: Connector) -> Optional[Dict[str, Any]]:
        """Get the metadata from the master branch."""
        response = requests.get(self._get_github_master_metadata_url(connector))
        
        if not response.ok:
            return None
        return yaml.safe_load(response.text)
    
    def _get_master_connector_version(self, connector: Connector) -> semver.Version:
        """Get the version from the master branch."""
        metadata = self._get_master_metadata(connector)
        if not metadata:
            return semver.Version.parse("0.0.0")
        
        return semver.Version.parse(str(metadata["data"]["dockerImageTag"]))
    
    def _get_current_connector_version(self, connector: Connector) -> semver.Version:
        """Get the current version."""
        return semver.Version.parse(str(connector.metadata["dockerImageTag"]))


class VersionIncrementCheck(VersionCheck):
    """Check that the connector version was incremented if files were modified."""
    
    @property
    def name(self) -> str:
        return "Connector Version Increment Check"
    
    @property
    def description(self) -> str:
        return "Validates that the connector version was incremented if files were modified."
    
    BYPASS_CHECK_FOR = [
        METADATA_FILE_NAME,
        "acceptance-test-config.yml",
        "README.md",
        "bootstrap.md",
        ".dockerignore",
        "unit_tests",
        "integration_tests",
        "src/test",
        "src/test-integration",
        "src/test-performance",
        "build.gradle",
        "erd",
        "build_customization.py",
    ]
    
    def _should_run(self, connector: Connector) -> bool:
        """Determine if the check should run based on modified files."""
        if connector.metadata and connector.metadata.get("ab_internal", {}).get("requireVersionIncrementsInPullRequests") is False:
            return False
        
        return True
    
    def _is_version_not_incremented(self, master_version: semver.Version, current_version: semver.Version) -> bool:
        """Check if the version was not incremented."""
        return master_version >= current_version
    
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
        if not self._should_run(connector):
            return self.skip(
                connector,
                "No modified files required a version bump or connector opts out of version checks."
            )
        
        try:
            master_version = self._get_master_connector_version(connector)
            current_version = self._get_current_connector_version(connector)
            
            if self._is_version_not_incremented(master_version, current_version):
                return self.fail(
                    connector,
                    f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented. "
                    f"Master version is {master_version}, current version is {current_version}"
                )
            
            if self._are_both_versions_release_candidates(master_version, current_version):
                if not self._have_same_major_minor_patch(master_version, current_version):
                    return self.fail(
                        connector,
                        f"Master and current version are release candidates but they have different major, minor or patch versions. "
                        f"Release candidates should only differ in the prerelease part. Master version is {master_version}, "
                        f"current version is {current_version}"
                    )
            
            return self.pass_(
                connector,
                f"Version was properly incremented from {master_version} to {current_version}."
            )
        except (requests.HTTPError, ValueError, TypeError) as e:
            return self.fail(connector, str(e))


ENABLED_CHECKS = [VersionIncrementCheck()]
