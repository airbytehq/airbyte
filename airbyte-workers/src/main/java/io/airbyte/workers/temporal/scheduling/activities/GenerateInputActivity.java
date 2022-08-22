/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class SyncInputWithAttemptNumber {

    private int attemptNumber;
    private long jobId;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class GeneratedJobInput {

    private JobRunConfig jobRunConfig;
    private IntegrationLauncherConfig sourceLauncherConfig;
    private IntegrationLauncherConfig destinationLauncherConfig;
    private StandardSyncInput syncInput;

  }

  /**
   * This generate the input needed by the child sync workflow
   */
  @ActivityMethod
  GeneratedJobInput getSyncWorkflowInput(SyncInput input);

  /**
   * This generate the input needed by the child sync workflow
   */
  @ActivityMethod
  GeneratedJobInput getSyncWorkflowInputWithAttemptNumber(SyncInputWithAttemptNumber input);

}
