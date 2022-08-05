/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.exception.RetryableException;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class GenerateInputActivityImpl implements GenerateInputActivity {

  private JobPersistence jobPersistence;

  @Override
  public SyncOutput getSyncWorkflowInput(final SyncInput input) {
    try {
      final long jobId = input.getJobId();
      final int attempt = input.getAttemptId();
      final JobSyncConfig config = jobPersistence.getJob(jobId).getConfig().getSync();

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
          .withResourceRequirements(config.getResourceRequirements());

      return new SyncOutput(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);
    } catch (final Exception e) {
      throw new RetryableException(e);
    }
  }

}
