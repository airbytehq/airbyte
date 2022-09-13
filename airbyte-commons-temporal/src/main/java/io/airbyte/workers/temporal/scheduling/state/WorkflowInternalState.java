/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.state;

import io.airbyte.config.FailureReason;
import java.util.HashSet;
import java.util.Set;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
public class WorkflowInternalState {

  private final Long jobId = null;
  private final Integer attemptNumber = null;

  // StandardSyncOutput standardSyncOutput = null;
  private final Set<FailureReason> failures = new HashSet<>();
  private final Boolean partialSuccess = null;

}
