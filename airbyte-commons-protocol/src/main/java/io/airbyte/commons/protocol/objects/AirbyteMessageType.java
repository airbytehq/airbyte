/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects;

public enum AirbyteMessageType {
  RECORD,
  STATE,
  LOG,
  CONNECTION_STATUS,
  CATALOG,
  TRACE,
  SPEC,
  CONTROL
}
