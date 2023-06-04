/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class BufferDequeueTest {

  public static final String RECORD_20_BYTES = "abc";
  private static final String STREAM_NAME = "stream1";
  private static final StreamDescriptor STREAM_DESC = new StreamDescriptor().withName(STREAM_NAME);
  private static final AirbyteMessage RECORD_MSG_20_BYTES = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withStream(STREAM_NAME)
          .withData(Jsons.jsonNode(RECORD_20_BYTES)));

  @Nested
  class Take {

    @Test
    void testTakeShouldBestEffortRead() {
      final BufferManager bufferManager = new BufferManager();
      final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
      final BufferDequeue dequeue = bufferManager.getBufferDequeue();

      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);

      // total size of records is 80, so we expect 50 to get us 2 records (prefer to under-pull records
      // than over-pull).
      try (final MemoryAwareMessageBatch take = dequeue.take(STREAM_DESC, 50)) {
        assertEquals(2, take.getData().toList().size());
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }

    @Test
    void testTakeShouldReturnAllIfPossible() {
      final BufferManager bufferManager = new BufferManager();
      final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
      final BufferDequeue dequeue = bufferManager.getBufferDequeue();

      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);

      try (final MemoryAwareMessageBatch take = dequeue.take(STREAM_DESC, 60)) {
        assertEquals(3, take.getData().toList().size());
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }

    @Test
    void testTakeFewerRecordsThanSizeLimitShouldNotError() {
      final BufferManager bufferManager = new BufferManager();
      final BufferEnqueue enqueue = bufferManager.getBufferEnqueue();
      final BufferDequeue dequeue = bufferManager.getBufferDequeue();

      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
      enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);

      try (final MemoryAwareMessageBatch take = dequeue.take(STREAM_DESC, Long.MAX_VALUE)) {
        assertEquals(2, take.getData().toList().size());
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

    enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);
    enqueue.addRecord(STREAM_DESC, RECORD_MSG_20_BYTES);

    final var secondStream = new StreamDescriptor().withName("stream_2");
    enqueue.addRecord(secondStream, RECORD_MSG_20_BYTES);

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
