/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;

public interface GetFileRecordWriter extends CheckedFunction<AirbyteStreamNameNamespacePair, String, Exception> {

  @Override
  String apply(AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair) throws Exception;
}
