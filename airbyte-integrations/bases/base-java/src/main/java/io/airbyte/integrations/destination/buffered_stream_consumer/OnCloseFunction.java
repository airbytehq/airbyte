/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedConsumer;

/**
 * Interface allowing destination to specify clean up logic that must be executed after all
 * record-related logic has finished.
 */
public interface OnCloseFunction extends CheckedConsumer<Boolean, Exception> {

  @Override
  void accept(Boolean hasFailed) throws Exception;

}
