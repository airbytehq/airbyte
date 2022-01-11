/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

public enum TemporalJobType {
  GET_SPEC,
  CHECK_CONNECTION,
  DISCOVER_SCHEMA,
  SYNC,
  RESET_CONNECTION,
  CONNECTION_UPDATER,
  REPLICATE
}
