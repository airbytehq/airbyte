/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.List;

public interface RecordWriter<T> extends CheckedBiConsumer<AirbyteStreamNameNamespacePair, List<T>, Exception> {

  @Override
  void accept(AirbyteStreamNameNamespacePair stream, List<T> records) throws Exception;

}
