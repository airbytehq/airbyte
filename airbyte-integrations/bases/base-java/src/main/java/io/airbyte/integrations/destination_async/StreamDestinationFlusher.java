/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.stream.Stream;

public interface StreamDestinationFlusher {

  // looking at SerializableBuffer, it seems getFile and getInputStream are both ways this can happen.
  void flush(StreamDescriptor decs, Stream<AirbyteMessage> stream) throws Exception;

  long getOptimalBatchSizeBytes();

}
