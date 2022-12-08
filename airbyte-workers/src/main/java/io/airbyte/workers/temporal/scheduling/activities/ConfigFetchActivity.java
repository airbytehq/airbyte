/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.io.IOException;
import java.time.Duration;
import java.util.Optional;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface ConfigFetchActivity {

  @ActivityMethod
  Optional<UUID> getSourceId(UUID connectionId);

  @ActivityMethod
  Optional<Status> getStatus(UUID connectionId);

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

    private Duration timeToWait;

  }

  StandardSync getStandardSync(final UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException;

  /**
   * Return how much time to wait before running the next sync. It will query the DB to get the last
   * starting time of the latest terminal job (Failed, canceled or successful) and return the amount
   * of second the Workflow needs to await.
   */
  @ActivityMethod
  ScheduleRetrieverOutput getTimeToWait(ScheduleRetrieverInput input);

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class GetMaxAttemptOutput {

    private int maxAttempt;

  }

  /**
   * Return the maximum number of attempt allowed for a connection.
   */
  @ActivityMethod
  GetMaxAttemptOutput getMaxAttempt();

}
