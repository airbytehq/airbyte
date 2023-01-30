/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.utils.ConfigReplacer;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
public class GenerateInputActivityImpl implements GenerateInputActivity {

  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private static final Logger LOGGER = LoggerFactory.getLogger(GenerateInputActivity.class);

  public GenerateInputActivityImpl(final JobPersistence jobPersistence,
                                   final ConfigRepository configRepository) {
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public GeneratedJobInput getSyncWorkflowInput(final SyncInput input) {
    final ConfigReplacer configReplacer = new ConfigReplacer(LOGGER);

    try {
      ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, input.getAttemptId(), JOB_ID_KEY, input.getJobId()));
      final long jobId = input.getJobId();
      final int attempt = input.getAttemptId();
      final JobSyncConfig config;

      final Job job = jobPersistence.getJob(jobId);
      final ConfigType jobConfigType = job.getConfig().getConfigType();
      if (ConfigType.SYNC.equals(jobConfigType)) {
        config = job.getConfig().getSync();
      } else if (ConfigType.RESET_CONNECTION.equals(jobConfigType)) {
        final JobResetConnectionConfig resetConnection = job.getConfig().getResetConnection();
        final ResetSourceConfiguration resetSourceConfiguration = resetConnection.getResetSourceConfiguration();
        config = new JobSyncConfig()
            .withNamespaceDefinition(resetConnection.getNamespaceDefinition())
            .withNamespaceFormat(resetConnection.getNamespaceFormat())
            .withPrefix(resetConnection.getPrefix())
            .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
            .withDestinationDockerImage(resetConnection.getDestinationDockerImage())
            .withDestinationProtocolVersion(resetConnection.getDestinationProtocolVersion())
            // null check for backwards compatibility with reset jobs that did not have a
            // resetSourceConfiguration
            .withSourceConfiguration(resetSourceConfiguration == null ? Jsons.emptyObject() : Jsons.jsonNode(resetSourceConfiguration))
            .withDestinationConfiguration(resetConnection.getDestinationConfiguration())
            .withConfiguredAirbyteCatalog(resetConnection.getConfiguredAirbyteCatalog())
            .withOperationSequence(resetConnection.getOperationSequence())
            .withResourceRequirements(resetConnection.getResourceRequirements())
            .withState(resetConnection.getState())
            .withIsSourceCustomConnector(resetConnection.getIsSourceCustomConnector())
            .withIsDestinationCustomConnector(resetConnection.getIsDestinationCustomConnector())
            .withWorkspaceId(resetConnection.getWorkspaceId());
      } else {
        throw new IllegalStateException(
            String.format("Unexpected config type %s for job %d. The only supported config types for this activity are (%s)",
                jobConfigType,
                jobId,
                List.of(ConfigType.SYNC, ConfigType.RESET_CONNECTION)));
      }

      final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);

      final UUID connectionId = UUID.fromString(job.getScope());
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);

      final StandardSourceDefinition sourceDefinition =
          configRepository.getSourceDefinitionFromSource(standardSync.getSourceId());

      final StandardDestinationDefinition destinationDefinition =
          configRepository.getDestinationDefinitionFromDestination(standardSync.getDestinationId());
      final String destinationNormalizationDockerImage = destinationDefinition.getNormalizationConfig() != null
          ? DockerUtils.getTaggedImageName(destinationDefinition.getNormalizationConfig().getNormalizationRepository(),
              destinationDefinition.getNormalizationConfig().getNormalizationTag())
          : null;
      final String normalizationIntegrationType =
          destinationDefinition.getNormalizationConfig() != null ? destinationDefinition.getNormalizationConfig().getNormalizationIntegrationType()
              : null;

      final IntegrationLauncherConfig sourceLauncherConfig = new IntegrationLauncherConfig()
          .withJobId(String.valueOf(jobId))
          .withAttemptId((long) attempt)
          .withDockerImage(config.getSourceDockerImage())
          .withProtocolVersion(config.getSourceProtocolVersion())
          .withIsCustomConnector(config.getIsSourceCustomConnector())
          .withAllowedHosts(ConfigType.RESET_CONNECTION.equals(jobConfigType) ? null
              : configReplacer.getAllowedHosts(sourceDefinition.getAllowedHosts(), config.getSourceConfiguration()));

      final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
          .withJobId(String.valueOf(jobId))
          .withAttemptId((long) attempt)
          .withDockerImage(config.getDestinationDockerImage())
          .withProtocolVersion(config.getDestinationProtocolVersion())
          .withIsCustomConnector(config.getIsDestinationCustomConnector())
          .withNormalizationDockerImage(destinationNormalizationDockerImage)
          .withSupportsDbt(destinationDefinition.getSupportsDbt())
          .withNormalizationIntegrationType(normalizationIntegrationType)
          .withAllowedHosts(configReplacer.getAllowedHosts(destinationDefinition.getAllowedHosts(), config.getDestinationConfiguration()));

      final StandardSyncInput syncInput = new StandardSyncInput()
          .withNamespaceDefinition(config.getNamespaceDefinition())
          .withNamespaceFormat(config.getNamespaceFormat())
          .withPrefix(config.getPrefix())
          .withSourceId(standardSync.getSourceId())
          .withDestinationId(standardSync.getDestinationId())
          .withSourceConfiguration(config.getSourceConfiguration())
          .withDestinationConfiguration(config.getDestinationConfiguration())
          .withOperationSequence(config.getOperationSequence())
          .withWebhookOperationConfigs(config.getWebhookOperationConfigs())
          .withCatalog(config.getConfiguredAirbyteCatalog())
          .withState(config.getState())
          .withResourceRequirements(config.getResourceRequirements())
          .withSourceResourceRequirements(config.getSourceResourceRequirements())
          .withDestinationResourceRequirements(config.getDestinationResourceRequirements())
          .withConnectionId(standardSync.getConnectionId())
          .withWorkspaceId(config.getWorkspaceId());

      return new GeneratedJobInput(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);

    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public GeneratedJobInput getSyncWorkflowInputWithAttemptNumber(final SyncInputWithAttemptNumber input) {
    ApmTraceUtils.addTagsToTrace(Map.of(JOB_ID_KEY, input.getJobId()));
    return getSyncWorkflowInput(new SyncInput(
        input.getAttemptNumber(),
        input.getJobId()));
  }

}
