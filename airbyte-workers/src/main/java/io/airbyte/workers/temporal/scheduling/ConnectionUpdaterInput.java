/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.workers.temporal.scheduling.state.WorkflowState;
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
  @Nullable
  private Integer attemptId;
  private boolean fromFailure;
  private int attemptNumber;
  @Nullable
  private WorkflowState workflowState;
  private boolean resetConnection;

}
