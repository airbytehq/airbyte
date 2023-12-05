/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.stream.Stream;

public interface RecordWriter<T> extends CheckedBiConsumer<AirbyteStreamNameNamespacePair, Stream<T>, Exception> {

  @Override
  void accept(AirbyteStreamNameNamespacePair stream, Stream<T> records) throws Exception;

}
