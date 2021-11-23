/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

  public static Set<JobStatus> TERMINAL_STATUSES = Sets.newHashSet(FAILED, SUCCEEDED, CANCELLED);

}
