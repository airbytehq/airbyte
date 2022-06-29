/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.sync.SyncWorkflow;
import io.temporal.api.enums.v1.RetryState;
import io.temporal.failure.ActivityFailure;
import java.util.UUID;

public class DbtFailureSyncWorkflow implements SyncWorkflow {

  // Should match activity types from FailureHelper.java
  private static final String ACTIVITY_TYPE_DBT_RUN = "Run";

  public static final Throwable CAUSE = new Exception("dbt failed");

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    throw new ActivityFailure(1L, 1L, ACTIVITY_TYPE_DBT_RUN, "someId", RetryState.RETRY_STATE_UNSPECIFIED, "someIdentity", CAUSE);
  }

}
