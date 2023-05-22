/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import org.junit.jupiter.api.Test;

public class BufferEnqueueTest {

  @Test
  void testAddRecordShouldAdd() {
    final var twoMB = 2 * 1024 * 1024;
    final var streamToBuffer = new ConcurrentHashMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>>();
    final var enqueue = new BufferEnqueue(new GlobalMemoryManager(twoMB), streamToBuffer);

    final var streamName = "stream";
    final var stream = new StreamDescriptor().withName(streamName);
    final var record = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withData(Jsons.jsonNode(BufferDequeueTest.RECORD_20_BYTES)));

    enqueue.addRecord(stream, record);
    assertEquals(1, streamToBuffer.get(stream).size());
    assertEquals(20L, streamToBuffer.get(stream).getCurrentMemoryUsage());

  }

  @Test
  public void testAddRecordShouldExpand() {
    final var oneKb = 1024;
    final var initialQueueSizeBytes = 20;
    final var streamToBuffer = new ConcurrentHashMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>>();
    final var enqueue = new BufferEnqueue(initialQueueSizeBytes, new GlobalMemoryManager(oneKb), streamToBuffer);

    final var streamName = "stream";
    final var stream = new StreamDescriptor().withName(streamName);
    final var record = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withData(Jsons.jsonNode(BufferDequeueTest.RECORD_20_BYTES)));

    enqueue.addRecord(stream, record);
    enqueue.addRecord(stream, record);
    assertEquals(2, streamToBuffer.get(stream).size());
    assertEquals(40, streamToBuffer.get(stream).getCurrentMemoryUsage());

  }

}
