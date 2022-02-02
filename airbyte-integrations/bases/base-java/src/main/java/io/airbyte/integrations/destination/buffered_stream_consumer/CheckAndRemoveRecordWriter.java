/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;

@FunctionalInterface
public interface CheckAndRemoveRecordWriter {

  String apply(AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair, String stagingFileName) throws Exception;

}
