/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

public enum Command {
  SPEC,
  CHECK,
  DISCOVER,
  READ,
  WRITE
}
