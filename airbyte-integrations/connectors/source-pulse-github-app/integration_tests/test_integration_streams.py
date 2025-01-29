import pytest
import time
import json
import os
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_pulse_github_app.source import SourcePulseGithubApp
from github import Github

@pytest.fixture
def config():
    """
    Reads the GitHub App config from secret/config.json, located in the root of the connector.
    Adjust the path logic below if your file structure differs.
    """
    connector_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    secret_config_path = os.path.join(connector_root, "secrets", "config.json")
    with open(secret_config_path, "r") as f:
        return json.load(f)


@pytest.mark.integration
def test_enterprise_orgs_stream_integration(config):
    # Only meaningful if is_enterprise = True
    # If you're not targeting enterprise, this might yield a single org or empty
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()

    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    # Use s.name (not s.name()) to match the class-level attribute
    enterprise_orgs_stream = next((s for s in streams if s.name == "enterprise_orgs"), None)
    assert enterprise_orgs_stream, "enterprise_orgs stream not found."

    slices = list(enterprise_orgs_stream.stream_slices(sync_mode=SyncMode.full_refresh))
    # enterprise_orgs might return no orgs if not an enterprise, but should not fail
    all_records = []
    for slice_ in slices:
        records = list(enterprise_orgs_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list)


@pytest.mark.integration
def test_org_members_stream_integration(config):
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    org_members = next((s for s in streams if s.name == "org_members"), None)
    assert org_members, "org_members stream not found."

    slices = list(org_members.stream_slices(sync_mode=SyncMode.full_refresh))
    assert len(slices) > 0, "Expected at least one slice from org_members"

    all_records = []
    for slice_ in slices:
        records = list(org_members.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list)


@pytest.mark.integration
def test_org_repos_stream_integration(config):
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    org_repos = next((s for s in streams if s.name == "org_repos"), None)
    assert org_repos, "org_repos stream not found."

    slices = list(org_repos.stream_slices(sync_mode=SyncMode.full_refresh))
    assert len(slices) > 0, "Expected at least one slice from org_repos"

    all_records = []
    for slice_ in slices:
        records = list(org_repos.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list)


@pytest.mark.integration
def test_repo_collaborators_stream_integration(config):
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    repo_collaborators = next((s for s in streams if s.name == "repo_collaborators"), None)
    assert repo_collaborators, "repo_collaborators stream not found."

    slices = list(repo_collaborators.stream_slices(sync_mode=SyncMode.full_refresh))
    assert len(slices) > 0, "Expected at least one slice from repo_collaborators"

    all_records = []
    for slice_ in slices:
        records = list(repo_collaborators.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list)


@pytest.mark.integration
def test_audit_logs_stream_integration(config):
    # Make sure your GitHub App has read:audit_log permission and that the
    # org_or_enterprise and start_date are set properly
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    audit_logs = next((s for s in streams if s.name == "audit_logs"), None)
    assert audit_logs, "audit_logs stream not found."

    slices = list(audit_logs.stream_slices(sync_mode=SyncMode.full_refresh))
    # If no audit logs available, might get no records, but test should not fail
    all_records = []
    for slice_ in slices:
        records = list(audit_logs.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list)


@pytest.mark.integration
def test_audit_logs_incremental_sync(config):
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    # First run: Full refresh
    streams = source.streams(config)
    audit_logs = next((s for s in streams if s.name == "audit_logs"), None)
    assert audit_logs, "audit_logs stream not found."

    # Run the first sync without state
    slices = list(audit_logs.stream_slices(sync_mode=SyncMode.full_refresh))
    all_records_first_run = []
    for slice_ in slices:
        records = list(audit_logs.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records_first_run.extend(records)

    # Ensure we got some records
    assert len(all_records_first_run) > 0, "No records returned in the first run. Can't test incremental sync."

    # Sort records by @timestamp to find the true maximum timestamp
    all_records_first_run.sort(key=lambda r: r["@timestamp"])

    # The highest timestamp is the last in the sorted list
    last_record = all_records_first_run[-1]
    last_timestamp = last_record["@timestamp"]
    assert isinstance(last_timestamp, int), "Expected @timestamp to be an int in milliseconds."

    # Create a state that represents having synced up to last_timestamp
    stream_state = {audit_logs.cursor_field: last_timestamp}

    logger.info(f"Performing an action on GitHub that generates audit logs...")
    perform_action_on_github_that_generates_audit_logs()

    # Wait 60 seconds for the audit log to record the action
    time.sleep(60)
    time.sleep(60)

    # Second run: Incremental
    # The stream supports incremental, but full_refresh calls also respect state in the CDK.
    # We'll explicitly use incremental for clarity.
    all_records_second_run = []
    for slice_ in slices:
        records = list(audit_logs.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice=slice_,
            stream_state=stream_state
        ))
        all_records_second_run.extend(records)

    # Verify that all returned records have @timestamp >= last_timestamp
    for record in all_records_second_run:
        assert record["@timestamp"] >= last_timestamp, (
            f"Incremental sync returned a record with @timestamp={record['@timestamp']} "
            f"not greater or equal than last state timestamp={last_timestamp}"
        )

    logger.info(f"Incremental sync test passed. {len(all_records_second_run)} newer records returned.")


def add_collaborator(repo_name, username, permission, token):
    logger = AirbyteLogger()
    g = Github(token)
    logger.info(f"Adding collaborator {username} to {repo_name}")
    repo = g.get_repo(repo_name)
    repo.add_to_collaborators(username, permission=permission)
    logger.info(f"Successfully added collaborator {username} to {repo_name}")


def remove_collaborator(repo_name, username, token):
    logger = AirbyteLogger()
    g = Github(token)
    logger.info(f"Removing collaborator {username} to {repo_name}")
    repo = g.get_repo(repo_name)
    repo.remove_from_collaborators(username)
    logger.info(f"Successfully removed collaborator {username} to {repo_name}")


def perform_action_on_github_that_generates_audit_logs():
    logger = AirbyteLogger()
    # Example usage
    token = "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"
    repo_name = "test-org-for-scim/meshulam"
    collaborator = "roncoco"
    permission = "push"

    add_collaborator(repo_name, collaborator, permission, token)
    time.sleep(60)
    remove_collaborator(repo_name, collaborator, token)


@pytest.mark.integration
def test_org_credential_authorizations_integration(config):
    """
    Test the org_credential_authorizations stream.
    Verifies that the connector can fetch OAuth tokens, SSH keys, etc.
    """
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    creds_stream = next((s for s in streams if s.name == "org_credential_authorizations"), None)
    assert creds_stream, "org_credential_authorizations stream not found."

    # Run full_refresh sync mode
    slices = list(creds_stream.stream_slices(sync_mode=SyncMode.full_refresh))
    all_records = []
    for slice_ in slices:
        records = list(creds_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list), "Records should be a list."
    # If no data is returned, that's not necessarily an error; as long as it doesn't crash, it's good.
    # If you know you have some, you can uncomment:
    # assert len(all_records) > 0, "Expected at least one credential authorization record."


@pytest.mark.integration
def test_org_installations_integration(config):
    """
    Test the org_installations stream.
    Verifies that the connector can list GitHub App installations in the organization.
    """
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    installations_stream = next((s for s in streams if s.name == "org_installations"), None)
    assert installations_stream, "org_installations stream not found."

    # Run full_refresh sync mode
    slices = list(installations_stream.stream_slices(sync_mode=SyncMode.full_refresh))
    all_records = []
    for slice_ in slices:
        records = list(installations_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    assert isinstance(all_records, list), "Records should be a list."
    # If you expect an installation, you could assert len(all_records) > 0

import pytest
import time
import json
import os
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_pulse_github_app.source import SourcePulseGithubApp


@pytest.mark.integration
def test_org_webhooks_stream_integration(config):
    """
    Test the org_webhooks stream.
    Ensures that the connector can list organization-level webhooks.
    """
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()

    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    org_webhooks_stream = next((s for s in streams if s.name == "org_webhooks"), None)
    assert org_webhooks_stream, "org_webhooks stream not found."

    # Generate all the slices we need to read
    slices = list(org_webhooks_stream.stream_slices(sync_mode=SyncMode.full_refresh))
    all_records = []

    # Iterate over each slice and collect records
    for slice_ in slices:
        records = list(org_webhooks_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    # Asserts
    assert isinstance(all_records, list), "Expected a list of org webhook records."
    # The org_webhooks stream might return zero webhooks if none exist in the org.
    # As long as it doesn't crash, it's still a pass.
    # If you expect at least one, you could assert len(all_records) > 0


@pytest.mark.integration
def test_repo_webhooks_stream_integration(config):
    """
    Test the repo_webhooks stream.
    Ensures that the connector can list repository-level webhooks.
    """
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()

    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    repo_webhooks_stream = next((s for s in streams if s.name == "repo_webhooks"), None)
    assert repo_webhooks_stream, "repo_webhooks stream not found."

    # Generate all the slices
    slices = list(repo_webhooks_stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert len(slices) > 0, "Expected at least one slice from repo_webhooks"

    all_records = []
    # Read and aggregate records across slices
    for slice_ in slices:
        records = list(repo_webhooks_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    # Asserts
    assert isinstance(all_records, list), "Expected a list of repo webhook records."
    # Similarly, you could optionally test for non-empty if you expect actual webhooks.

@pytest.mark.integration
def test_repo_workflow_runs_stream_integration(config):
    """
    Test the repo_workflow_runs stream:
    Ensures that the connector can list workflow runs for each repo,
    along with their job steps.
    """
    logger = AirbyteLogger()
    source = SourcePulseGithubApp()
    success, error = source.check_connection(logger, config)
    assert success, f"Connection check failed: {error}"

    streams = source.streams(config)
    workflow_runs_stream = next((s for s in streams if s.name == "repo_workflow_runs"), None)
    assert workflow_runs_stream, "repo_workflow_runs stream not found."

    slices = list(workflow_runs_stream.stream_slices(sync_mode=SyncMode.full_refresh))
    assert len(slices) > 0, "Expected at least one slice from repo_workflow_runs"

    all_records = []
    for slice_ in slices:
        records = list(workflow_runs_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
        all_records.extend(records)

    # Make sure we got a list of records (possibly zero if no runs in the repo).
    assert isinstance(all_records, list), "Expected a list of workflow run records."

    # Optional: If you expect at least one run in your test org, you could:
    # assert len(all_records) > 0, "Expected at least one workflow run."

    # If you want to test that steps are populated:
    for run_record in all_records:
        # run_record["jobs"] is attached in the stream code above
        assert "jobs" in run_record, "Expected 'jobs' key in the run record."
        # Each job might have an array of steps
        # e.g., run_record["jobs"] = [{"steps": [...]}]
        # but it can also be empty if no steps exist or run is queued, etc.
