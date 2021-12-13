/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.time.Duration;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface ConfigFetchActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class ScheduleRetrieverInput {

    private UUID connectionId;

  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class ScheduleRetrieverOutput {

    private Duration periodicity;

  }

  @ActivityMethod
  ScheduleRetrieverOutput getPeriodicity(ScheduleRetrieverInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class GetMaxAttemptOutput {

    private int maxAttempt;

  }

  @ActivityMethod
  GetMaxAttemptOutput getMaxAttempt();

}
