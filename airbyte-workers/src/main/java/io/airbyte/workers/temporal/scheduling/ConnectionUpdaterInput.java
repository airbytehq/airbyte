/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.JobConfig;
import java.util.Optional;
import java.util.UUID;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ConnectionUpdaterInput {

  private UUID connectionId;
  private Optional<Long> jobId;
  private JobConfig jobConfig;
  private Optional<Integer> attemptId;
  private boolean fromFailure;

}
