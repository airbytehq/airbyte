/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;

public interface FlushBufferFunction extends CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> {

  @Override
  void accept(AirbyteStreamNameNamespacePair stream, SerializableBuffer buffer) throws Exception;

}
