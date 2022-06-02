/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

import com.google.common.collect.Sets;
import java.util.Set;

public enum JobStatus {

  PENDING,
  RUNNING,
  INCOMPLETE,
  FAILED,
  SUCCEEDED,
  CANCELLED;

  public static final Set<JobStatus> TERMINAL_STATUSES = Sets.newHashSet(FAILED, SUCCEEDED, CANCELLED);
  public static final Set<JobStatus> NON_TERMINAL_STATUSES = Sets.difference(Set.of(values()), TERMINAL_STATUSES);

}
