/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.BufferManager.BufferManagerDequeue;
import io.airbyte.integrations.destination_async.BufferManager.BufferManagerDequeue.Batch;
import io.airbyte.integrations.destination_async.BufferManager.BufferManagerEnqueue;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.junit.jupiter.api.Test;

public class BufferManagerDequeueTest {

  private static final String STREAM_NAME = "stream1";
  private static final StreamDescriptor STREAM_DESC = new StreamDescriptor().withName(STREAM_NAME);
  private static final String RECORD = "abc";
  private static final AirbyteMessage RECORD_MSG = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withStream(STREAM_NAME)
          .withData(Jsons.jsonNode(RECORD)));

  @Test
  void testReadFromBatch() {
    final BufferManager bufferManager = new BufferManager();
    final BufferManagerEnqueue enqueue = bufferManager.getBufferManagerEnqueue();
    final BufferManagerDequeue dequeue = bufferManager.getBufferManagerDequeue();

    enqueue.addRecord(STREAM_DESC, RECORD_MSG);
    enqueue.addRecord(STREAM_DESC, RECORD_MSG);
    enqueue.addRecord(STREAM_DESC, RECORD_MSG);
    enqueue.addRecord(STREAM_DESC, RECORD_MSG);

    // total size of records is 80, so we expect 50 to get us 2 records (prefer to under-pull records
    // than over-pull).
    try (final Batch take = dequeue.take(STREAM_DESC, 50)) {
      assertEquals(2, take.getData().toList().size());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  void testReadFromBatchFewerRecordsThanSizeLimit() {
    final BufferManager bufferManager = new BufferManager();
    final BufferManagerEnqueue enqueue = bufferManager.getBufferManagerEnqueue();
    final BufferManagerDequeue dequeue = bufferManager.getBufferManagerDequeue();

    enqueue.addRecord(STREAM_DESC, RECORD_MSG);
    enqueue.addRecord(STREAM_DESC, RECORD_MSG);

    try (final Batch take = dequeue.take(STREAM_DESC, Long.MAX_VALUE)) {
      assertEquals(2, take.getData().toList().size());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
