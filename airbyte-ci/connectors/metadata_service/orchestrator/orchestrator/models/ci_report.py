from dataclasses import dataclass
from typing import Optional

# TODO (ben): When the pipeline project is brought into the airbyte-ci folder
# we should update these models to import their twin models from the pipeline project


@dataclass(frozen=True)
class ConnectorNightlyReport:
    file_path: str
    pipeline_name: Optional[str] = None
    run_timestamp: Optional[str] = None
    run_duration: Optional[float] = None
    success: Optional[bool] = None
    failed_steps: Optional[list] = None
    successful_steps: Optional[list] = None
    skipped_steps: Optional[list] = None
    gha_workflow_run_url: Optional[str] = None
    pipeline_start_timestamp: Optional[int] = None
    pipeline_end_timestamp: Optional[int] = None
    pipeline_duration: Optional[int] = None
    git_branch: Optional[str] = None
    git_revision: Optional[str] = None
    ci_context: Optional[str] = None
    pull_request_url: Optional[str] = None


@dataclass(frozen=True)
class ConnectorPipelineReport:
    file_path: str
    connector_technical_name: Optional[str] = None
    connector_version: Optional[str] = None
    run_timestamp: Optional[str] = None
    run_duration: Optional[float] = None
    success: Optional[bool] = None
    failed_steps: Optional[list] = None
    successful_steps: Optional[list] = None
    skipped_steps: Optional[list] = None
    gha_workflow_run_url: Optional[str] = None
    pipeline_start_timestamp: Optional[int] = None
    pipeline_end_timestamp: Optional[int] = None
    pipeline_duration: Optional[int] = None
    git_branch: Optional[str] = None
    git_revision: Optional[str] = None
    ci_context: Optional[str] = None
    cdk_version: Optional[str] = None
