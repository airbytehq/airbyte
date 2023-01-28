/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.AttemptApi;
import io.airbyte.api.client.generated.StateApi;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateType;
import io.airbyte.api.client.model.generated.SaveAttemptSyncConfigRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.converters.ApiPojoConverters;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.ActorType;
import io.airbyte.config.AttemptSyncConfig;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.State;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.helper.StateConverter;
import io.airbyte.workers.utils.ConfigReplacer;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
public class GenerateInputActivityImpl implements GenerateInputActivity {

  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final AttemptApi attemptApi;
  private final StateApi stateApi;
  private final FeatureFlags featureFlags;

  public GenerateInputActivityImpl(final JobPersistence jobPersistence,
                                   final ConfigRepository configRepository,
                                   final StateApi stateApi,
                                   final AttemptApi attemptApi,
                                   final FeatureFlags featureFlags) {
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.stateApi = stateApi;
    this.attemptApi = attemptApi;
    this.featureFlags = featureFlags;
  }

  private Optional<State> getCurrentConnectionState(final UUID connectionId) {
    final ConnectionState state = AirbyteApiClient.retryWithJitter(
        () -> stateApi.getState(new ConnectionIdRequestBody().connectionId(connectionId)),
        "get state");

    if (state.getStateType() == ConnectionStateType.NOT_SET)
      return Optional.empty();

    final StateWrapper internalState = StateConverter.clientToInternal(state);
    return Optional.of(StateMessageHelper.getState(internalState));
  }

  private void saveAttemptSyncConfig(final long jobId, final int attemptNumber, final UUID connectionId, final AttemptSyncConfig attemptSyncConfig) {
    AirbyteApiClient.retryWithJitter(
        () -> attemptApi.saveSyncConfig(new SaveAttemptSyncConfigRequestBody()
            .jobId(jobId)
            .attemptNumber(attemptNumber)
            .syncConfig(ApiPojoConverters.attemptSyncConfigToClient(attemptSyncConfig, connectionId, featureFlags.useStreamCapableState()))),
        "set attempt sync config");
  }

  @Override
  public SyncJobCheckConnectionInputs getCheckConnectionInputs(final SyncInputWithAttemptNumber input) {
    final long jobId = input.getJobId();
    final int attemptNumber = input.getAttemptNumber();

    try {
      final Job job = jobPersistence.getJob(jobId);
      final JobSyncConfig jobSyncConfig = getJobSyncConfig(jobId, job.getConfig());

      final UUID connectionId = UUID.fromString(job.getScope());
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);

      final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());
      final StandardDestinationDefinition destinationDefinition =
          configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());

      final SourceConnection source = configRepository.getSourceConnection(standardSync.getSourceId());
      final StandardSourceDefinition sourceDefinition =
          configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());

      final IntegrationLauncherConfig sourceLauncherConfig = getSourceIntegrationLauncherConfig(
          jobId,
          attemptNumber,
          jobSyncConfig,
          sourceDefinition,
          source.getConfiguration());

      final IntegrationLauncherConfig destinationLauncherConfig =
          getDestinationIntegrationLauncherConfig(
              jobId,
              attemptNumber,
              jobSyncConfig,
              destinationDefinition,
              destination.getConfiguration());

      final StandardCheckConnectionInput sourceCheckConnectionInput = new StandardCheckConnectionInput()
          .withActorType(ActorType.SOURCE)
          .withActorId(source.getSourceId())
          .withConnectionConfiguration(source.getConfiguration());

      final StandardCheckConnectionInput destinationCheckConnectionInput = new StandardCheckConnectionInput()
          .withActorType(ActorType.DESTINATION)
          .withActorId(destination.getDestinationId())
          .withConnectionConfiguration(destination.getConfiguration());

      return new SyncJobCheckConnectionInputs(
          sourceLauncherConfig,
          destinationLauncherConfig,
          sourceCheckConnectionInput,
          destinationCheckConnectionInput);

    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

  private IntegrationLauncherConfig getSourceIntegrationLauncherConfig(final long jobId,
                                                                       final int attempt,
                                                                       final JobSyncConfig config,
                                                                       final StandardSourceDefinition sourceDefinition,
                                                                       final JsonNode sourceConfiguration)
      throws IOException {
    final ConfigReplacer configReplacer = new ConfigReplacer();
    return new IntegrationLauncherConfig()
        .withJobId(String.valueOf(jobId))
        .withAttemptId((long) attempt)
        .withDockerImage(config.getSourceDockerImage())
        .withProtocolVersion(config.getSourceProtocolVersion())
        .withIsCustomConnector(config.getIsSourceCustomConnector())
        .withAllowedHosts(configReplacer.getAllowedHosts(sourceDefinition.getAllowedHosts(), sourceConfiguration));
  }

  private IntegrationLauncherConfig getDestinationIntegrationLauncherConfig(final long jobId,
                                                                            final int attempt,
                                                                            final JobSyncConfig config,
                                                                            final StandardDestinationDefinition destinationDefinition,
                                                                            final JsonNode destinationConfiguration)
      throws IOException {
    final ConfigReplacer configReplacer = new ConfigReplacer();
    final String destinationNormalizationDockerImage = destinationDefinition.getNormalizationConfig() != null
        ? DockerUtils.getTaggedImageName(destinationDefinition.getNormalizationConfig().getNormalizationRepository(),
            destinationDefinition.getNormalizationConfig().getNormalizationTag())
        : null;
    final String normalizationIntegrationType =
        destinationDefinition.getNormalizationConfig() != null ? destinationDefinition.getNormalizationConfig().getNormalizationIntegrationType()
            : null;

    return new IntegrationLauncherConfig()
        .withJobId(String.valueOf(jobId))
        .withAttemptId((long) attempt)
        .withDockerImage(config.getDestinationDockerImage())
        .withProtocolVersion(config.getDestinationProtocolVersion())
        .withIsCustomConnector(config.getIsDestinationCustomConnector())
        .withNormalizationDockerImage(destinationNormalizationDockerImage)
        .withSupportsDbt(destinationDefinition.getSupportsDbt())
        .withNormalizationIntegrationType(normalizationIntegrationType)
        .withAllowedHosts(configReplacer.getAllowedHosts(destinationDefinition.getAllowedHosts(), destinationConfiguration));
  }

  /**
   * Returns a Job's JobSyncConfig, converting it from a JobResetConnectionConfig if necessary.
   */
  private JobSyncConfig getJobSyncConfig(final long jobId, final JobConfig jobConfig) {
    final ConfigType jobConfigType = jobConfig.getConfigType();
    if (ConfigType.SYNC.equals(jobConfigType)) {
      return jobConfig.getSync();
    } else if (ConfigType.RESET_CONNECTION.equals(jobConfigType)) {
      final JobResetConnectionConfig resetConnection = jobConfig.getResetConnection();

      return new JobSyncConfig()
          .withNamespaceDefinition(resetConnection.getNamespaceDefinition())
          .withNamespaceFormat(resetConnection.getNamespaceFormat())
          .withPrefix(resetConnection.getPrefix())
          .withSourceDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB)
          .withDestinationDockerImage(resetConnection.getDestinationDockerImage())
          .withDestinationProtocolVersion(resetConnection.getDestinationProtocolVersion())
          .withConfiguredAirbyteCatalog(resetConnection.getConfiguredAirbyteCatalog())
          .withOperationSequence(resetConnection.getOperationSequence())
          .withResourceRequirements(resetConnection.getResourceRequirements())
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
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public GeneratedJobInput getSyncWorkflowInput(final SyncInput input) {
    try {
      ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, input.getAttemptId(), JOB_ID_KEY, input.getJobId()));
      final long jobId = input.getJobId();
      final int attempt = input.getAttemptId();

      final Job job = jobPersistence.getJob(jobId);
      final JobSyncConfig config = getJobSyncConfig(jobId, job.getConfig());

      final UUID connectionId = UUID.fromString(job.getScope());
      final StandardSync standardSync = configRepository.getStandardSync(connectionId);

      final AttemptSyncConfig attemptSyncConfig = new AttemptSyncConfig();
      getCurrentConnectionState(connectionId).ifPresent(attemptSyncConfig::setState);

      final ConfigType jobConfigType = job.getConfig().getConfigType();
      if (ConfigType.SYNC.equals(jobConfigType)) {
        final SourceConnection source = configRepository.getSourceConnection(standardSync.getSourceId());
        attemptSyncConfig.setSourceConfiguration(source.getConfiguration());
      } else if (ConfigType.RESET_CONNECTION.equals(jobConfigType)) {
        final JobResetConnectionConfig resetConnection = job.getConfig().getResetConnection();
        final ResetSourceConfiguration resetSourceConfiguration = resetConnection.getResetSourceConfiguration();
        attemptSyncConfig
            .setSourceConfiguration(resetSourceConfiguration == null ? Jsons.emptyObject() : Jsons.jsonNode(resetSourceConfiguration));
      }

      final JobRunConfig jobRunConfig = TemporalWorkflowUtils.createJobRunConfig(jobId, attempt);

      final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());
      attemptSyncConfig.setDestinationConfiguration(destination.getConfiguration());

      final StandardSourceDefinition sourceDefinition =
          configRepository.getSourceDefinitionFromSource(standardSync.getSourceId());

      final StandardDestinationDefinition destinationDefinition =
          configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());

      final IntegrationLauncherConfig sourceLauncherConfig = getSourceIntegrationLauncherConfig(
          jobId,
          attempt,
          config,
          sourceDefinition,
          attemptSyncConfig.getSourceConfiguration());

      final IntegrationLauncherConfig destinationLauncherConfig = getDestinationIntegrationLauncherConfig(
          jobId,
          attempt,
          config,
          destinationDefinition,
          attemptSyncConfig.getDestinationConfiguration());

      final StandardSyncInput syncInput = new StandardSyncInput()
          .withNamespaceDefinition(config.getNamespaceDefinition())
          .withNamespaceFormat(config.getNamespaceFormat())
          .withPrefix(config.getPrefix())
          .withSourceId(standardSync.getSourceId())
          .withDestinationId(standardSync.getDestinationId())
          .withSourceConfiguration(attemptSyncConfig.getSourceConfiguration())
          .withDestinationConfiguration(attemptSyncConfig.getDestinationConfiguration())
          .withOperationSequence(config.getOperationSequence())
          .withWebhookOperationConfigs(config.getWebhookOperationConfigs())
          .withCatalog(config.getConfiguredAirbyteCatalog())
          .withState(attemptSyncConfig.getState())
          .withResourceRequirements(config.getResourceRequirements())
          .withSourceResourceRequirements(config.getSourceResourceRequirements())
          .withDestinationResourceRequirements(config.getDestinationResourceRequirements())
          .withWorkspaceId(config.getWorkspaceId());

      saveAttemptSyncConfig(jobId, attempt, connectionId, attemptSyncConfig);

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
