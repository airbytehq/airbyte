/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

public enum TemporalJobType {
  GET_SPEC,
  CHECK_CONNECTION,
  DISCOVER_SCHEMA,
  SYNC,
  RESET_CONNECTION,
  CONNECTION_UPDATER,
  REPLICATE,
  NOTIFY
}
