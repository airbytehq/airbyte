/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import edu.umd.cs.findbugs.annotations.Nullable;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.WebUrlHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
  private static final String WORKSPACE_ID_META_KEY = "workspace_id";
  private static final String WORKSPACE_URL_META_KEY = "workspace_url";
  private static final String CONNECTION_ID_META_KEY = "connection_id";
  private static final String CONNECTION_URL_META_KEY = "connection_url";
  private static final String CONNECTOR_NAME_META_KEY = "connector_name";
  private static final String CONNECTOR_REPOSITORY_META_KEY = "connector_repository";
  private static final String CONNECTOR_DEFINITION_ID_META_KEY = "connector_definition_id";
  private static final String CONNECTOR_RELEASE_STAGE_META_KEY = "connector_release_stage";
  private static final String CONNECTOR_COMMAND_META_KEY = "connector_command";
  private static final String NORMALIZATION_REPOSITORY_META_KEY = "normalization_repository";
  private static final String JOB_ID_KEY = "job_id";

  private final ConfigRepository configRepository;
  private final DeploymentMode deploymentMode;
  private final String airbyteVersion;
  private final String normalizationImage;
  private final String normalizationVersion;
  private final WebUrlHelper webUrlHelper;
  private final JobErrorReportingClient jobErrorReportingClient;

  public JobErrorReporter(final ConfigRepository configRepository,
                          final DeploymentMode deploymentMode,
                          final String airbyteVersion,
                          final String normalizationImage,
                          final String normalizationVersion,
                          final WebUrlHelper webUrlHelper,
                          final JobErrorReportingClient jobErrorReportingClient) {

    this.configRepository = configRepository;
    this.deploymentMode = deploymentMode;
    this.airbyteVersion = airbyteVersion;
    this.normalizationImage = normalizationImage;
    this.normalizationVersion = normalizationVersion;
    this.webUrlHelper = webUrlHelper;
    this.jobErrorReportingClient = jobErrorReportingClient;
  }

  /**
   * Reports a Sync Job's connector-caused FailureReasons to the JobErrorReportingClient
   *
   * @param connectionId - connection that had the failure
   * @param failureSummary - final attempt failure summary
   * @param jobContext - sync job reporting context
   */
  public void reportSyncJobFailure(final UUID connectionId, final AttemptFailureSummary failureSummary, final SyncJobReportingContext jobContext) {
    Exceptions.swallow(() -> {
      final List<FailureReason> traceMessageFailures = failureSummary.getFailures().stream()
          .filter(failure -> failure.getMetadata() != null && failure.getMetadata().getAdditionalProperties().containsKey(FROM_TRACE_MESSAGE))
          .toList();

      final StandardWorkspace workspace = configRepository.getStandardWorkspaceFromConnection(connectionId, true);
      final Map<String, String> commonMetadata = MoreMaps.merge(
          Map.of(JOB_ID_KEY, String.valueOf(jobContext.jobId())),
          getConnectionMetadata(workspace.getWorkspaceId(), connectionId));

      for (final FailureReason failureReason : traceMessageFailures) {
        final FailureOrigin failureOrigin = failureReason.getFailureOrigin();

        if (failureOrigin == FailureOrigin.SOURCE) {
          final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromConnection(connectionId);
          final String dockerImage = jobContext.sourceDockerImage();
          final Map<String, String> metadata = MoreMaps.merge(commonMetadata, getSourceMetadata(sourceDefinition));

          reportJobFailureReason(workspace, failureReason, dockerImage, metadata);
        } else if (failureOrigin == FailureOrigin.DESTINATION) {
          final StandardDestinationDefinition destinationDefinition = configRepository.getDestinationDefinitionFromConnection(connectionId);
          final String dockerImage = jobContext.destinationDockerImage();
          final Map<String, String> metadata = MoreMaps.merge(commonMetadata, getDestinationMetadata(destinationDefinition));

          reportJobFailureReason(workspace, failureReason, dockerImage, metadata);
        } else if (failureOrigin == FailureOrigin.NORMALIZATION) {
          final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromConnection(connectionId);
          final StandardDestinationDefinition destinationDefinition = configRepository.getDestinationDefinitionFromConnection(connectionId);
          // since error could be arising from source or destination or normalization itself, we want all the
          // metadata
          // prefixing source keys so we don't overlap (destination as 'true' keys since normalization runs on
          // the destination)
          final Map<String, String> metadata = MoreMaps.merge(
              commonMetadata,
              getNormalizationMetadata(),
              prefixConnectorMetadataKeys(getSourceMetadata(sourceDefinition), "source"),
              getDestinationMetadata(destinationDefinition));
          final String dockerImage = String.format("%s:%s", normalizationImage, normalizationVersion);

          reportJobFailureReason(workspace, failureReason, dockerImage, metadata);
        }
      }
    });
  }

  /**
   * Reports a FailureReason from a connector Check job for a Source to the JobErrorReportingClient
   *
   * @param workspaceId - workspace for which the check failed
   * @param failureReason - failure reason from the check connection job
   * @param jobContext - connector job reporting context
   */
  public void reportSourceCheckJobFailure(final UUID sourceDefinitionId,
                                          final UUID workspaceId,
                                          final FailureReason failureReason,
                                          final ConnectorJobReportingContext jobContext)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspace(workspaceId, true);
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final Map<String, String> metadata = MoreMaps.merge(
        getSourceMetadata(sourceDefinition),
        Map.of(JOB_ID_KEY, jobContext.jobId().toString()));
    reportJobFailureReason(workspace, failureReason.withFailureOrigin(FailureOrigin.SOURCE), jobContext.dockerImage(), metadata);
  }

  /**
   * Reports a FailureReason from a connector Check job for a Destination to the
   * JobErrorReportingClient
   *
   * @param workspaceId - workspace for which the check failed
   * @param failureReason - failure reason from the check connection job
   * @param jobContext - connector job reporting context
   */
  public void reportDestinationCheckJobFailure(final UUID destinationDefinitionId,
                                               final UUID workspaceId,
                                               final FailureReason failureReason,
                                               final ConnectorJobReportingContext jobContext)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspace(workspaceId, true);
    final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    final Map<String, String> metadata = MoreMaps.merge(
        getDestinationMetadata(destinationDefinition),
        Map.of(JOB_ID_KEY, jobContext.jobId().toString()));
    reportJobFailureReason(workspace, failureReason.withFailureOrigin(FailureOrigin.DESTINATION), jobContext.dockerImage(), metadata);
  }

  /**
   * Reports a FailureReason from a connector Deploy job for a Source to the JobErrorReportingClient
   *
   * @param workspaceId - workspace for which the Discover job failed
   * @param failureReason - failure reason from the Discover job
   * @param jobContext - connector job reporting context
   */
  public void reportDiscoverJobFailure(final UUID sourceDefinitionId,
                                       final UUID workspaceId,
                                       final FailureReason failureReason,
                                       final ConnectorJobReportingContext jobContext)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = configRepository.getStandardWorkspace(workspaceId, true);
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final Map<String, String> metadata = MoreMaps.merge(
        getSourceMetadata(sourceDefinition),
        Map.of(JOB_ID_KEY, jobContext.jobId().toString()));
    reportJobFailureReason(workspace, failureReason, jobContext.dockerImage(), metadata);
  }

  /**
   * Reports a FailureReason from a connector Spec job to the JobErrorReportingClient
   *
   * @param failureReason - failure reason from the Deploy job
   * @param jobContext - connector job reporting context
   */
  public void reportSpecJobFailure(final FailureReason failureReason, final ConnectorJobReportingContext jobContext) {
    final String dockerImage = jobContext.dockerImage();
    final String connectorRepository = dockerImage.split(":")[0];
    final Map<String, String> metadata = Map.of(
        JOB_ID_KEY, jobContext.jobId().toString(),
        CONNECTOR_REPOSITORY_META_KEY, connectorRepository);
    reportJobFailureReason(null, failureReason, dockerImage, metadata);
  }

  private Map<String, String> getConnectionMetadata(final UUID workspaceId, final UUID connectionId) {
    final String connectionUrl = webUrlHelper.getConnectionUrl(workspaceId, connectionId);
    return Map.ofEntries(
        Map.entry(CONNECTION_ID_META_KEY, connectionId.toString()),
        Map.entry(CONNECTION_URL_META_KEY, connectionUrl));
  }

  private Map<String, String> getDestinationMetadata(final StandardDestinationDefinition destinationDefinition) {
    return Map.ofEntries(
        Map.entry(CONNECTOR_DEFINITION_ID_META_KEY, destinationDefinition.getDestinationDefinitionId().toString()),
        Map.entry(CONNECTOR_NAME_META_KEY, destinationDefinition.getName()),
        Map.entry(CONNECTOR_REPOSITORY_META_KEY, destinationDefinition.getDockerRepository()),
        Map.entry(CONNECTOR_RELEASE_STAGE_META_KEY, destinationDefinition.getReleaseStage().value()));
  }

  private Map<String, String> getSourceMetadata(final StandardSourceDefinition sourceDefinition) {
    return Map.ofEntries(
        Map.entry(CONNECTOR_DEFINITION_ID_META_KEY, sourceDefinition.getSourceDefinitionId().toString()),
        Map.entry(CONNECTOR_NAME_META_KEY, sourceDefinition.getName()),
        Map.entry(CONNECTOR_REPOSITORY_META_KEY, sourceDefinition.getDockerRepository()),
        Map.entry(CONNECTOR_RELEASE_STAGE_META_KEY, sourceDefinition.getReleaseStage().value()));
  }

  private Map<String, String> getNormalizationMetadata() {
    return Map.ofEntries(
        Map.entry(NORMALIZATION_REPOSITORY_META_KEY, normalizationImage));
  }

  private Map<String, String> prefixConnectorMetadataKeys(final Map<String, String> connectorMetadata, final String prefix) {
    final Map<String, String> prefixedMetadata = new HashMap<>();
    for (final Map.Entry<String, String> entry : connectorMetadata.entrySet()) {
      prefixedMetadata.put(String.format("%s_%s", prefix, entry.getKey()), entry.getValue());
    }
    return prefixedMetadata;
  }

  private Map<String, String> getFailureReasonMetadata(final FailureReason failureReason) {
    final Map<String, Object> failureReasonAdditionalProps = failureReason.getMetadata().getAdditionalProperties();
    final Map<String, String> outMetadata = new HashMap<>();

    if (failureReasonAdditionalProps.containsKey(CONNECTOR_COMMAND_META_KEY)
        && failureReasonAdditionalProps.get(CONNECTOR_COMMAND_META_KEY) != null) {
      outMetadata.put(CONNECTOR_COMMAND_META_KEY, failureReasonAdditionalProps.get(CONNECTOR_COMMAND_META_KEY).toString());
    }

    if (failureReason.getFailureOrigin() != null) {
      outMetadata.put(FAILURE_ORIGIN_META_KEY, failureReason.getFailureOrigin().value());
    }

    if (failureReason.getFailureType() != null) {
      outMetadata.put(FAILURE_TYPE_META_KEY, failureReason.getFailureType().value());
    }

    return outMetadata;
  }

  private Map<String, String> getWorkspaceMetadata(final UUID workspaceId) {
    final String workspaceUrl = webUrlHelper.getWorkspaceUrl(workspaceId);
    return Map.ofEntries(
        Map.entry(WORKSPACE_ID_META_KEY, workspaceId.toString()),
        Map.entry(WORKSPACE_URL_META_KEY, workspaceUrl));
  }

  private void reportJobFailureReason(@Nullable final StandardWorkspace workspace,
                                      final FailureReason failureReason,
                                      final String dockerImage,
                                      final Map<String, String> metadata) {
    final Map<String, String> commonMetadata = new HashMap<>(Map.ofEntries(
        Map.entry(AIRBYTE_VERSION_META_KEY, airbyteVersion),
        Map.entry(DEPLOYMENT_MODE_META_KEY, deploymentMode.name())));

    if (workspace != null) {
      commonMetadata.putAll(getWorkspaceMetadata(workspace.getWorkspaceId()));
    }

    final Map<String, String> allMetadata = MoreMaps.merge(
        commonMetadata,
        getFailureReasonMetadata(failureReason),
        metadata);

    try {
      jobErrorReportingClient.reportJobFailureReason(workspace, failureReason, dockerImage, allMetadata);
    } catch (final Exception e) {
      LOGGER.error("Error when reporting job failure reason: {}", failureReason, e);
    }
  }

}
