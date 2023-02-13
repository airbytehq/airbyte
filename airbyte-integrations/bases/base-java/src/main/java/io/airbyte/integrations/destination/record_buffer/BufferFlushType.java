/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

public enum BufferFlushType {
  FLUSH_ALL,
  FLUSH_SINGLE_STREAM
}
