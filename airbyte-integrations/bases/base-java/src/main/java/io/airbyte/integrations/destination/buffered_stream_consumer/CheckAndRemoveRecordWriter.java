/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;

@FunctionalInterface
public interface CheckAndRemoveRecordWriter {

  /**
   * Compares the name of the current staging file with the method argument. If the names are
   * different, then the staging writer corresponding to `stagingFileName` is closed and the name of
   * the new file where the record will be sent will be returned.
   */
  String apply(AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair, String stagingFileName) throws Exception;

}
