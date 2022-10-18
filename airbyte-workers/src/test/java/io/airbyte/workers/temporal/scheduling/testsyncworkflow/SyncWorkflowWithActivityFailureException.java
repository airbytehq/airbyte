/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.api.enums.v1.RetryState;
import io.temporal.failure.ActivityFailure;
import io.temporal.workflow.Workflow;
import java.util.UUID;

/**
 * Test sync that simulate an activity failure of the child workflow.
 */
public class SyncWorkflowWithActivityFailureException implements SyncWorkflow {

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {
    Workflow.sleep(SleepingSyncWorkflow.RUN_TIME);
    throw new ActivityFailure(1L, 1L, "Replication", "id", RetryState.RETRY_STATE_RETRY_POLICY_NOT_SET,
        "identity",
        new Exception("Error"));
  }

}
