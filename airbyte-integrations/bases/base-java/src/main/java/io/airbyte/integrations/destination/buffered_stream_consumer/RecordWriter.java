/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import java.util.List;

public interface RecordWriter<T> extends CheckedBiConsumer<AirbyteStreamNameNamespacePair, List<T>, Exception> {

  @Override
  void accept(AirbyteStreamNameNamespacePair pair, List<T> records) throws Exception;

}
