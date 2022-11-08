/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling.state;

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

  private Long jobId = null;
  private Integer attemptNumber = null;

  // StandardSyncOutput standardSyncOutput = null;
  private Set<FailureReason> failures = new HashSet<>();
  private Boolean partialSuccess = null;

}
