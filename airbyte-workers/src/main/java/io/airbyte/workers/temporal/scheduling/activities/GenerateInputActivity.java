/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface GenerateInputActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class SyncInput {

    private int attemptId;
    private long jobId;
    private boolean reset;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class SyncOutput {

    private JobRunConfig jobRunConfig;
    private IntegrationLauncherConfig sourceLauncherConfig;
    private IntegrationLauncherConfig destinationLauncherConfig;
    private StandardSyncInput syncInput;

  }

  /**
   * This generate the input needed by the child sync workflow
   */
  @ActivityMethod
  SyncOutput getSyncWorkflowInput(SyncInput input);

}
