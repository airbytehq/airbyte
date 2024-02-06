/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import io.airbyte.cdk.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteRecordMessage;
import io.airbyte.cdk.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import org.junit.jupiter.api.Test;

public class BufferEnqueueTest {

  private static final int RECORD_SIZE_20_BYTES = 20;
  private static final String DEFAULT_NAMESPACE = "foo_namespace";

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

    enqueue.addRecord(record, RECORD_SIZE_20_BYTES, DEFAULT_NAMESPACE);
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

    enqueue.addRecord(record, RECORD_SIZE_20_BYTES, DEFAULT_NAMESPACE);
    enqueue.addRecord(record, RECORD_SIZE_20_BYTES, DEFAULT_NAMESPACE);
    assertEquals(2, streamToBuffer.get(stream).size());
    assertEquals(40, streamToBuffer.get(stream).getCurrentMemoryUsage());

  }

}
