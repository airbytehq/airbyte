/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobErrorReporter {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobErrorReporter.class);

  private static final String FROM_TRACE_MESSAGE = "from_trace_message";
  private static final String DEPLOYMENT_MODE_META_KEY = "deployment_mode";
  private static final String AIRBYTE_VERSION_META_KEY = "airbyte_version";
  private static final String FAILURE_ORIGIN_META_KEY = "failure_origin";
  private static final String FAILURE_TYPE_META_KEY = "failure_type";
  private static final String CONNECTION_ID_META_KEY = "connection_id";
  private static final String CONNECTOR_NAME_META_KEY = "connector_name";
  private static final String CONNECTOR_DEFINITION_ID_META_KEY = "connector_definition_id";
  private static final String CONNECTOR_RELEASE_STAGE_META_KEY = "connector_release_stage";

  private final ConfigRepository configRepository;
  private final DeploymentMode deploymentMode;
  private final String airbyteVersion;
  private final JobErrorReportingClient jobErrorReportingClient;

  public JobErrorReporter(final ConfigRepository configRepository,
                          final DeploymentMode deploymentMode,
                          final String airbyteVersion,
                          final JobErrorReportingClient jobErrorReportingClient) {

    this.configRepository = configRepository;
    this.deploymentMode = deploymentMode;
    this.airbyteVersion = airbyteVersion;
    this.jobErrorReportingClient = jobErrorReportingClient;
  }

  /**
   * Reports a Sync Job's connector-caused FailureReasons to the JobErrorReportingClient
   *
   * @param connectionId - connection that had the failure
   * @param failureSummary - final attempt failure summary
   * @param jobSyncConfig - config for the sync job
   */
  public void reportSyncJobFailure(final UUID connectionId, final AttemptFailureSummary failureSummary, final JobSyncConfig jobSyncConfig) {
    final List<FailureReason> traceMessageFailures = failureSummary.getFailures().stream()
        .filter(failure -> failure.getMetadata() != null && failure.getMetadata().getAdditionalProperties().containsKey(FROM_TRACE_MESSAGE))
        .toList();

    final StandardWorkspace workspace = configRepository.getStandardWorkspaceFromConnection(connectionId, true);

    for (final FailureReason failureReason : traceMessageFailures) {
      final FailureOrigin failureOrigin = failureReason.getFailureOrigin();

      final HashMap<String, String> metadata = new HashMap<>();
      metadata.put(CONNECTION_ID_META_KEY, connectionId.toString());
      metadata.put(AIRBYTE_VERSION_META_KEY, airbyteVersion);
      metadata.put(DEPLOYMENT_MODE_META_KEY, deploymentMode.name());
      metadata.put(FAILURE_ORIGIN_META_KEY, failureOrigin.value());
      metadata.put(FAILURE_TYPE_META_KEY, failureReason.getFailureType().value());

      try {
        if (failureOrigin == FailureOrigin.SOURCE) {
          final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromConnection(connectionId);
          final String dockerImage = jobSyncConfig.getSourceDockerImage();

          metadata.put(CONNECTOR_DEFINITION_ID_META_KEY, sourceDefinition.getSourceDefinitionId().toString());
          metadata.put(CONNECTOR_NAME_META_KEY, sourceDefinition.getName());
          metadata.put(CONNECTOR_RELEASE_STAGE_META_KEY, sourceDefinition.getReleaseStage().value());

          jobErrorReportingClient.reportJobFailureReason(workspace, failureReason, dockerImage, metadata);
        } else if (failureOrigin == FailureOrigin.DESTINATION) {
          final StandardDestinationDefinition destinationDefinition = configRepository.getDestinationDefinitionFromConnection(connectionId);
          final String dockerImage = jobSyncConfig.getDestinationDockerImage();

          metadata.put(CONNECTOR_DEFINITION_ID_META_KEY, destinationDefinition.getDestinationDefinitionId().toString());
          metadata.put(CONNECTOR_NAME_META_KEY, destinationDefinition.getName());
          metadata.put(CONNECTOR_RELEASE_STAGE_META_KEY, destinationDefinition.getReleaseStage().value());

          jobErrorReportingClient.reportJobFailureReason(workspace, failureReason, dockerImage, metadata);
        }
      } catch (final Exception e) {
        LOGGER.error("Error when reporting job failure reason: {}", failureReason, e);
      }
    }
  }

}
