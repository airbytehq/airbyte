/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.JobConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface GetSyncInputActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class Input {

    private int attemptId;
    private long jobId;
    private JobConfig jobConfig;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class Output {

    private JobRunConfig jobRunConfig;
    private IntegrationLauncherConfig sourceLauncherConfig;
    private IntegrationLauncherConfig destinationLauncherConfig;
    private StandardSyncInput syncInput;

  }

  @ActivityMethod
  Output getSyncWorkflowInput(Input input);

}
