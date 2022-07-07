/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.exception.RetryableException;
import java.util.List;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class GenerateInputActivityImpl implements GenerateInputActivity {

  private JobPersistence jobPersistence;

  @Override
  public GeneratedJobInput getSyncWorkflowInput(final SyncInput input) {
    try {
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
            // null check for backwards compatibility with reset jobs that did not have a
            // resetSourceConfiguration
            .withSourceConfiguration(resetSourceConfiguration == null ? Jsons.emptyObject() : Jsons.jsonNode(resetSourceConfiguration))
            .withDestinationConfiguration(resetConnection.getDestinationConfiguration())
            .withConfiguredAirbyteCatalog(resetConnection.getConfiguredAirbyteCatalog())
            .withOperationSequence(resetConnection.getOperationSequence())
            .withResourceRequirements(resetConnection.getResourceRequirements())
            .withState(resetConnection.getState());
      } else {
        throw new IllegalStateException(
            String.format("Unexpected config type %s for job %d. The only supported config types for this activity are (%s)",
                jobConfigType,
                jobId,
                List.of(ConfigType.SYNC, ConfigType.RESET_CONNECTION)));
      }

      final JobRunConfig jobRunConfig = TemporalUtils.createJobRunConfig(jobId, attempt);

      final IntegrationLauncherConfig sourceLauncherConfig = new IntegrationLauncherConfig()
          .withJobId(String.valueOf(jobId))
          .withAttemptId((long) attempt)
          .withDockerImage(config.getSourceDockerImage());

      final IntegrationLauncherConfig destinationLauncherConfig = new IntegrationLauncherConfig()
          .withJobId(String.valueOf(jobId))
          .withAttemptId((long) attempt)
          .withDockerImage(config.getDestinationDockerImage());

      final StandardSyncInput syncInput = new StandardSyncInput()
          .withNamespaceDefinition(config.getNamespaceDefinition())
          .withNamespaceFormat(config.getNamespaceFormat())
          .withPrefix(config.getPrefix())
          .withSourceConfiguration(config.getSourceConfiguration())
          .withDestinationConfiguration(config.getDestinationConfiguration())
          .withOperationSequence(config.getOperationSequence())
          .withCatalog(config.getConfiguredAirbyteCatalog())
          .withState(config.getState())
          .withResourceRequirements(config.getResourceRequirements())
          .withSourceResourceRequirements(config.getSourceResourceRequirements())
          .withDestinationResourceRequirements(config.getDestinationResourceRequirements());

      return new GeneratedJobInput(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);

    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public GeneratedJobInput getSyncWorkflowInputWithAttemptNumber(final SyncInputWithAttemptNumber input) {
    return getSyncWorkflowInput(new SyncInput(
        input.getAttemptNumber(),
        input.getJobId()));
  }

}
