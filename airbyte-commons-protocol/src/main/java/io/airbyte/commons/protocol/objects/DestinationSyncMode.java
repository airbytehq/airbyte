/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects;

public enum DestinationSyncMode {
  APPEND,
  OVERWRITE,
  APPEND_DEDUP
}
