#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

import pytest
import semver
from base_images import version_registry
from base_images.python.bases import AirbytePythonConnectorBaseImage


class TestChangelogEntry:
    def test_to_serializable_dict(self):
        changelog_entry = version_registry.ChangelogEntry(semver.VersionInfo.parse("1.0.0"), "first version", "Dockerfile example")
        assert (
            json.dumps(changelog_entry.to_serializable_dict())
            == '{"version": "1.0.0", "changelog_entry": "first version", "dockerfile_example": "Dockerfile example"}'
        ), "The changelog entry should be serializable to JSON"


class TestVersionRegistry:
    @pytest.fixture
    def fake_entries(self, mocker):
        # Please keep this list ordered by version
        return [
            version_registry.VersionRegistryEntry(
                published_docker_image=mocker.Mock(), changelog_entry="first version", version=semver.VersionInfo.parse("1.0.0")
            ),
            version_registry.VersionRegistryEntry(
                published_docker_image=mocker.Mock(), changelog_entry="second version", version=semver.VersionInfo.parse("2.0.0")
            ),
            version_registry.VersionRegistryEntry(
                published_docker_image=mocker.Mock(), changelog_entry="pre-release", version=semver.VersionInfo.parse("3.0.0-rc.1")
            ),
            version_registry.VersionRegistryEntry(
                published_docker_image=None, changelog_entry="third version", version=semver.VersionInfo.parse("3.0.0")
            ),
        ]

    def test_entries(self, fake_entries):
        entries = version_registry.VersionRegistry(AirbytePythonConnectorBaseImage, fake_entries).entries
        versions = [entry.version for entry in entries]
        assert set(versions) == set(
            [entry.version for entry in fake_entries]
        ), "The entries should be unique by version and contain all the entries passed as argument"
        assert versions == sorted(versions, reverse=True), "The entries should be sorted by version in descending order"

    def test_latest_entry(self, fake_entries):
        vr = version_registry.VersionRegistry(AirbytePythonConnectorBaseImage, fake_entries)
        assert vr.latest_entry == fake_entries[-1]

    def test_get_entry_for_version(self, fake_entries):
        vr = version_registry.VersionRegistry(AirbytePythonConnectorBaseImage, fake_entries)
        entry = vr.get_entry_for_version(semver.VersionInfo.parse("1.0.0"))
        assert entry.version == semver.VersionInfo.parse("1.0.0")

    def test_latest_published_entry(self, fake_entries):
        vr = version_registry.VersionRegistry(AirbytePythonConnectorBaseImage, fake_entries)
        assert vr.latest_published_entry == fake_entries[-2]

    def latest_not_pre_released_published_entry(self, fake_entries):
        vr = version_registry.VersionRegistry(AirbytePythonConnectorBaseImage, fake_entries)
        assert vr.latest_not_pre_released_published_entry == fake_entries[1]

    def test_get_changelog_dump_path(self, mocker):
        mock_connector_class = mocker.Mock()
        mock_connector_class.repository = "example-repo"

        path = version_registry.VersionRegistry.get_changelog_dump_path(mock_connector_class)
        expected_changelog_dump_path = Path("generated/changelogs/example_repo.json")
        assert path == expected_changelog_dump_path
        assert version_registry.VersionRegistry(mock_connector_class, []).changelog_dump_path == expected_changelog_dump_path

    def test_get_changelog_entries_with_existing_json(self, mocker, tmp_path):
        dummy_change_log_path = tmp_path / "changelog.json"
        dummy_changelog_entry = version_registry.ChangelogEntry(semver.VersionInfo.parse("1.0.0"), "Initial release", "")
        dummy_change_log_path.write_text(json.dumps([dummy_changelog_entry.to_serializable_dict()]))

        mock_connector_class = mocker.Mock()
        mocker.patch.object(version_registry.VersionRegistry, "get_changelog_dump_path", return_value=dummy_change_log_path)

        changelog_entries = version_registry.VersionRegistry.get_changelog_entries(mock_connector_class)

        assert len(changelog_entries) == 1
        assert isinstance(changelog_entries[0], version_registry.ChangelogEntry)
        assert changelog_entries[0].version == semver.VersionInfo.parse("1.0.0")
        assert changelog_entries[0].changelog_entry == "Initial release"

    def test_get_changelog_entries_without_json(self, mocker, tmp_path):
        dummy_change_log_path = tmp_path / "changelog.json"

        mock_connector_class = mocker.Mock()
        mocker.patch.object(version_registry.VersionRegistry, "get_changelog_dump_path", return_value=dummy_change_log_path)

        changelog_entries = version_registry.VersionRegistry.get_changelog_entries(mock_connector_class)
        assert len(changelog_entries) == 0

    @pytest.fixture
    def mock_dagger_client(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def fake_docker_credentials(self):
        return ("username", "password")

    @pytest.fixture
    def fake_changelog_entries(self):
        return [
            version_registry.ChangelogEntry(semver.VersionInfo.parse("1.0.0"), "first version", ""),
            version_registry.ChangelogEntry(semver.VersionInfo.parse("2.0.0"), "second unpublished version", ""),
        ]

    @pytest.fixture
    def fake_published_images(self, mocker):
        # Mock the published images to include only one version (2.0.0)
        return [mocker.Mock(version=semver.VersionInfo.parse("1.0.0"))]

    @pytest.mark.anyio
    async def test_get_all_published_base_images(self, mocker, mock_dagger_client, fake_docker_credentials):
        mock_crane_client = mocker.Mock()
        mocker.patch.object(version_registry.docker, "CraneClient", return_value=mock_crane_client)

        mock_remote_registry = mocker.AsyncMock()
        mocker.patch.object(version_registry.docker, "RemoteRepository", return_value=mock_remote_registry)

        sample_published_images = [mocker.Mock(), mocker.Mock()]
        mock_remote_registry.get_all_images.return_value = sample_published_images

        published_images = await version_registry.VersionRegistry.get_all_published_base_images(
            mock_dagger_client, fake_docker_credentials, mocker.Mock()
        )

        assert published_images == sample_published_images

    @pytest.mark.anyio
    async def test_load_with_mocks(
        self, mocker, mock_dagger_client, fake_docker_credentials, fake_changelog_entries, fake_published_images
    ):
        mocker.patch.object(version_registry.VersionRegistry, "get_changelog_entries", return_value=fake_changelog_entries)
        mocker.patch.object(version_registry.VersionRegistry, "get_all_published_base_images", return_value=fake_published_images)

        registry = await version_registry.VersionRegistry.load(mocker.Mock(), mock_dagger_client, fake_docker_credentials)

        assert len(registry.entries) == 2, "Two entries should be in the registry"
        version_1_entry = registry.get_entry_for_version(semver.VersionInfo.parse("1.0.0"))
        assert version_1_entry is not None, "The version 1.0.0 should be in the registry even if not published"
        assert version_1_entry.published, "The version 1.0.0 should be published"
        version_2_entry = registry.get_entry_for_version(semver.VersionInfo.parse("2.0.0"))
        assert version_2_entry is not None, "The version 2.0.0 should be in the registry even if not published"
        assert version_2_entry.published is False, "The version 2.0.0 should not be published"
