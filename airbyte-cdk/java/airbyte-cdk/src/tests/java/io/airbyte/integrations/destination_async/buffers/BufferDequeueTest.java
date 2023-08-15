/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class BufferDequeueTest {

  private static final int RECORD_SIZE_20_BYTES = 20;
  public static final String RECORD_20_BYTES = "abc";
  private static final String STREAM_NAME = "stream1";
  private static final StreamDescriptor STREAM_DESC = new StreamDescriptor().withName(STREAM_NAME);
  private static final PartialAirbyteMessage RECORD_MSG_20_BYTES = new PartialAirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new PartialAirbyteRecordMessage()
          .withStream(STREAM_NAME));

  @Nested
  class Take {

    @Test
    void testTakeShouldBestEffortRead() {
      final BufferManager bufferManager = new BufferManager();
      final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
      final BufferDequeue dequeue = bufferManager.getBufferDequeue();

      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);

      // total size of records is 80, so we expect 50 to get us 2 records (prefer to under-pull records
      // than over-pull).
      try (final MemoryAwareMessageBatch take = dequeue.take(STREAM_DESC, 50)) {
        assertEquals(2, take.getData().size());
        // verify it only took the records from the queue that it actually returned.
        assertEquals(2, dequeue.getQueueSizeInRecords(STREAM_DESC).orElseThrow());
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }

    @Test
    void testTakeShouldReturnAllIfPossible() {
      final BufferManager bufferManager = new BufferManager();
      final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
      final BufferDequeue dequeue = bufferManager.getBufferDequeue();

      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);

      try (final MemoryAwareMessageBatch take = dequeue.take(STREAM_DESC, 60)) {
        assertEquals(3, take.getData().size());
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }

    @Test
    void testTakeFewerRecordsThanSizeLimitShouldNotError() {
      final BufferManager bufferManager = new BufferManager();
      final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
      final BufferDequeue dequeue = bufferManager.getBufferDequeue();

      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
      enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);

      try (final MemoryAwareMessageBatch take = dequeue.take(STREAM_DESC, Long.MAX_VALUE)) {
        assertEquals(2, take.getData().size());
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }

  }

  @Test
  void testMetadataOperationsCorrect() {
    final BufferManager bufferManager = new BufferManager();
    final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
    final BufferDequeue dequeue = bufferManager.getBufferDequeue();

    enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);
    enqueue.addRecord(RECORD_MSG_20_BYTES, RECORD_SIZE_20_BYTES);

    final var secondStream = new StreamDescriptor().withName("stream_2");
    final PartialAirbyteMessage recordFromSecondStream = Jsons.clone(RECORD_MSG_20_BYTES);
    recordFromSecondStream.getRecord().withStream(secondStream.getName());
    enqueue.addRecord(recordFromSecondStream, RECORD_SIZE_20_BYTES);

    assertEquals(60, dequeue.getTotalGlobalQueueSizeBytes());

    assertEquals(2, dequeue.getQueueSizeInRecords(STREAM_DESC).get());
    assertEquals(1, dequeue.getQueueSizeInRecords(secondStream).get());

    assertEquals(40, dequeue.getQueueSizeBytes(STREAM_DESC).get());
    assertEquals(20, dequeue.getQueueSizeBytes(secondStream).get());

    // Buffer of 3 sec to deal with test execution variance.
    final var lastThreeSec = Instant.now().minus(3, ChronoUnit.SECONDS);
    assertTrue(lastThreeSec.isBefore(dequeue.getTimeOfLastRecord(STREAM_DESC).get()));
    assertTrue(lastThreeSec.isBefore(dequeue.getTimeOfLastRecord(secondStream).get()));
  }

  @Test
  void testMetadataOperationsError() {
    final BufferManager bufferManager = new BufferManager();
    final BufferDequeue dequeue = bufferManager.getBufferDequeue();

    final var ghostStream = new StreamDescriptor().withName("ghost stream");

    assertEquals(0, dequeue.getTotalGlobalQueueSizeBytes());

    assertTrue(dequeue.getQueueSizeInRecords(ghostStream).isEmpty());

    assertTrue(dequeue.getQueueSizeBytes(ghostStream).isEmpty());

    assertTrue(dequeue.getTimeOfLastRecord(ghostStream).isEmpty());
  }

}
