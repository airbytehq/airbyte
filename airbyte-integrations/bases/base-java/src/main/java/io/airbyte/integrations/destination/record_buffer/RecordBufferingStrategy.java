/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteMessage;

public interface RecordBufferingStrategy extends AutoCloseable {

  void addRecord(AirbyteStreamNameNamespacePair stream, AirbyteMessage message) throws Exception;

  void flushWriter(AirbyteStreamNameNamespacePair stream, RecordBufferImplementation writer) throws Exception;

  void flushAll() throws Exception;

  void clear() throws Exception;

  void registerFlushEventHook(VoidCallable onFlushEventHook);

}
