/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedConsumer;

public interface OnCloseFunction extends CheckedConsumer<Boolean, Exception> {

  @Override
  void accept(Boolean hasFailed) throws Exception;

}
