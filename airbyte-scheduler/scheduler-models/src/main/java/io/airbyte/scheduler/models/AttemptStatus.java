/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

import com.google.common.collect.Sets;
import java.util.Set;

public enum AttemptStatus {

  RUNNING,
  FAILED,
  SUCCEEDED;

  public static final Set<AttemptStatus> TERMINAL_STATUSES = Sets.newHashSet(FAILED, SUCCEEDED);

}
