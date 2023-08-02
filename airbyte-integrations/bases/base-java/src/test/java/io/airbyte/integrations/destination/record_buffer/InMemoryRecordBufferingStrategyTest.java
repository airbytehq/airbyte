/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

public class InMemoryRecordBufferingStrategyTest {

  private static final JsonNode MESSAGE_DATA = Jsons.deserialize("{ \"field1\": 10000 }");
  // MESSAGE_DATA should be 64 bytes long, size the buffer such as it can contain at least 2 message
  // instances
  private static final int MAX_QUEUE_SIZE_IN_BYTES = 130;

  @SuppressWarnings("unchecked")
  private final RecordWriter<AirbyteRecordMessage> recordWriter = mock(RecordWriter.class);

  @Test
  public void testBuffering() throws Exception {
    final InMemoryRecordBufferingStrategy buffering = new InMemoryRecordBufferingStrategy(recordWriter, MAX_QUEUE_SIZE_IN_BYTES);
    final AirbyteStreamNameNamespacePair stream1 = new AirbyteStreamNameNamespacePair("stream1", "namespace");
    final AirbyteStreamNameNamespacePair stream2 = new AirbyteStreamNameNamespacePair("stream2", null);
    final AirbyteMessage message1 = generateMessage(stream1);
    final AirbyteMessage message2 = generateMessage(stream2);
    final AirbyteMessage message3 = generateMessage(stream2);
    final AirbyteMessage message4 = generateMessage(stream2);

    assertFalse(buffering.addRecord(stream1, message1).isPresent());
    assertFalse(buffering.addRecord(stream2, message2).isPresent());
    // Buffer still has room
    final Optional<BufferFlushType> flushType = buffering.addRecord(stream2, message3);
    // Keeps track of this #addRecord since we're expecting a buffer flush & that the flushType
    // value will indicate that all buffers were flushed
    assertTrue(flushType.isPresent());
    assertEquals(flushType.get(), BufferFlushType.FLUSH_ALL);
    // Buffer limit reach, flushing all messages so far before adding the new incoming one
    verify(recordWriter, times(1)).accept(stream1, List.of(message1.getRecord()));
    verify(recordWriter, times(1)).accept(stream2, List.of(message2.getRecord()));

    buffering.addRecord(stream2, message4);

    // force flush to terminate test
    buffering.flushAllBuffers();
    verify(recordWriter, times(1)).accept(stream2, List.of(message3.getRecord(), message4.getRecord()));
  }

  private static AirbyteMessage generateMessage(final AirbyteStreamNameNamespacePair stream) {
    return new AirbyteMessage().withRecord(new AirbyteRecordMessage()
        .withStream(stream.getName())
        .withNamespace(stream.getNamespace())
        .withData(MESSAGE_DATA));
  }

}
