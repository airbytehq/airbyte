/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.config.JobConfig;
import java.util.UUID;
import javax.annotation.Nullable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.NonNull;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ConnectionUpdaterInput {

  @NonNull
  private UUID connectionId;
  @Nullable
  private Long jobId;
  @NonNull
  private JobConfig jobConfig;
  @Nullable
  private Integer attemptId;
  @NonNull
  private boolean fromFailure;

}
