/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

public enum ErrorCode {
  UNKNOWN,
  WORKFLOW_DELETED,
  WORKFLOW_RUNNING
}
