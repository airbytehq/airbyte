/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

public enum Command {
  SPEC,
  CHECK,
  DISCOVER,
  READ,
  WRITE
}
