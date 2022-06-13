package io.airbyte.scheduler.persistence;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.scheduler.persistence.error_reporting.ErrorReportingClient;
import java.util.List;
import java.util.UUID;

public class JobErrorReporter {
  
  private final ConfigPersistence configPersistence;
  private final WorkspaceHelper workspaceHelper;
  private final ErrorReportingClient errorReportingClient;

  public JobErrorReporter(
      final ConfigPersistence configPersistence,
      final WorkspaceHelper workspaceHelper,
      final ErrorReportingClient errorReportingClient) {

    this.configPersistence = configPersistence;
    this.workspaceHelper = workspaceHelper;
    this.errorReportingClient = errorReportingClient;
  }

  public void reportSyncJobFailure(final AttemptFailureSummary failureSummary, final UUID connectionId, final JobSyncConfig job) {

    // airbyte/source-marketo:0.11 -- what happens if not semver? e.g: custom tag or "latest" or "dev"
    // connector_definition_id, docker_image_name+version, connection_id, connection_id, workspace_id
    // do something like this to get cert level -- configPersistence.getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, "<>", );

    final UUID workspaceId = workspaceHelper.getWorkspaceForConnectionIdIgnoreExceptions(connectionId);
    final List<FailureReason> sourceFailures = failureSummary.getFailures().stream()
        .filter(failure -> failure.getFailureOrigin() == FailureOrigin.SOURCE).toList();
    final List<FailureReason> destinationFailures = failureSummary.getFailures().stream()
        .filter(failure -> failure.getFailureOrigin() == FailureOrigin.DESTINATION).toList();

    for (final FailureReason sourceFailure : sourceFailures) {
      // report failure about source
      errorReportingClient.report();
    }

    for (final FailureReason destinationFailure : destinationFailures) {
      // report failure about destination
      errorReportingClient.report();
    }
  }
}
