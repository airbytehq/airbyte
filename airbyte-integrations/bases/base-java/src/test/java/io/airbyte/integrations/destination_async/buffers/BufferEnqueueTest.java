/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteRecordMessage;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import org.junit.jupiter.api.Test;

public class BufferEnqueueTest {

  private static final int RECORD_SIZE_20_BYTES = 20;

  @Test
  void testAddRecordShouldAdd() {
    final var twoMB = 2 * 1024 * 1024;
    final var streamToBuffer = new ConcurrentHashMap<StreamDescriptor, StreamAwareQueue>();
    final var enqueue = new BufferEnqueue(new GlobalMemoryManager(twoMB), streamToBuffer, mock(GlobalAsyncStateManager.class));

    final var streamName = "stream";
    final var stream = new StreamDescriptor().withName(streamName);
    final var record = new PartialAirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream(streamName));

    enqueue.addRecord(record, RECORD_SIZE_20_BYTES);
    assertEquals(1, streamToBuffer.get(stream).size());
    assertEquals(20L, streamToBuffer.get(stream).getCurrentMemoryUsage());

  }

  @Test
  public void testAddRecordShouldExpand() {
    final var oneKb = 1024;
    final var streamToBuffer = new ConcurrentHashMap<StreamDescriptor, StreamAwareQueue>();
    final var enqueue =
        new BufferEnqueue(new GlobalMemoryManager(oneKb), streamToBuffer, mock(GlobalAsyncStateManager.class));

    final var streamName = "stream";
    final var stream = new StreamDescriptor().withName(streamName);
    final var record = new PartialAirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream(streamName));

    enqueue.addRecord(record, RECORD_SIZE_20_BYTES);
    enqueue.addRecord(record, RECORD_SIZE_20_BYTES);
    assertEquals(2, streamToBuffer.get(stream).size());
    assertEquals(40, streamToBuffer.get(stream).getCurrentMemoryUsage());

  }

}
