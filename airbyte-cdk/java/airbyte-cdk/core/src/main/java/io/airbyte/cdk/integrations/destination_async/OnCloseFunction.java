/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async;

import java.util.function.Consumer;

/**
 * Async version of
 * {@link io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction}.
 * Separately out for easier versioning.
 */
public interface OnCloseFunction extends Consumer<Boolean> {
  static OnCloseFunction fromNonAsync(final io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction legacy) {
    return (success) -> {
      try {
        legacy.accept(success);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    };
  }
}
