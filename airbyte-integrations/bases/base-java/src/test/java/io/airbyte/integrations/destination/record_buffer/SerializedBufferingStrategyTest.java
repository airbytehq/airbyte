/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SerializedBufferingStrategyTest {

  private static final JsonNode MESSAGE_DATA = Jsons.deserialize("{ \"field1\": 10000 }");
  private static final String STREAM_1 = "stream1";
  private static final String STREAM_2 = "stream2";
  private static final String STREAM_3 = "stream3";
  private static final String STREAM_4 = "stream4";

  // we set the limit to hold at most 4 messages of 10b total
  private static final long MAX_TOTAL_BUFFER_SIZE_BYTES = 42L;
  // we set the limit to hold at most 2 messages of 10b per stream
  private static final long MAX_PER_STREAM_BUFFER_SIZE_BYTES = 21L;

  private final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
  @SuppressWarnings("unchecked")
  private final CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> perStreamFlushHook =
      mock(CheckedBiConsumer.class);

  private final SerializableBuffer recordWriter1 = mock(SerializableBuffer.class);
  private final SerializableBuffer recordWriter2 = mock(SerializableBuffer.class);
  private final SerializableBuffer recordWriter3 = mock(SerializableBuffer.class);
  private final SerializableBuffer recordWriter4 = mock(SerializableBuffer.class);

  @BeforeEach
  public void setup() throws Exception {
    setupMock(recordWriter1);
    setupMock(recordWriter2);
    setupMock(recordWriter3);
    setupMock(recordWriter4);
  }

  private void setupMock(final SerializableBuffer mockObject) throws Exception {
    when(mockObject.accept(any())).thenReturn(10L);
    when(mockObject.getByteCount()).thenReturn(10L);
    when(mockObject.getMaxTotalBufferSizeInBytes()).thenReturn(MAX_TOTAL_BUFFER_SIZE_BYTES);
    when(mockObject.getMaxPerStreamBufferSizeInBytes()).thenReturn(MAX_PER_STREAM_BUFFER_SIZE_BYTES);
    when(mockObject.getMaxConcurrentStreamsInBuffer()).thenReturn(4);
  }

  @Test
  public void testPerStreamThresholdFlush() throws Exception {
    final SerializedBufferingStrategy buffering = new SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook);
    final AirbyteStreamNameNamespacePair stream1 = new AirbyteStreamNameNamespacePair(STREAM_1, "namespace");
    final AirbyteStreamNameNamespacePair stream2 = new AirbyteStreamNameNamespacePair(STREAM_2, null);
    // To test per stream threshold, we are sending multiple test messages on a single stream
    final AirbyteMessage message1 = generateMessage(stream1);
    final AirbyteMessage message2 = generateMessage(stream2);
    final AirbyteMessage message3 = generateMessage(stream2);
    final AirbyteMessage message4 = generateMessage(stream2);
    final AirbyteMessage message5 = generateMessage(stream2);

    when(recordWriter1.getByteCount()).thenReturn(10L); // one record in recordWriter1
    assertFalse(buffering.addRecord(stream1, message1).isPresent());
    when(recordWriter2.getByteCount()).thenReturn(10L); // one record in recordWriter2
    assertFalse(buffering.addRecord(stream2, message2).isPresent());

    // Total and per stream Buffers still have room
    verify(perStreamFlushHook, times(0)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(0)).accept(stream2, recordWriter2);

    when(recordWriter2.getByteCount()).thenReturn(20L); // second record in recordWriter2
    assertFalse(buffering.addRecord(stream2, message3).isPresent());
    when(recordWriter2.getByteCount()).thenReturn(30L); // third record in recordWriter2

    // Buffer reaches limit so a buffer flush occurs returning a buffer flush type of single stream
    final Optional<BufferFlushType> flushType = buffering.addRecord(stream2, message4);
    assertTrue(flushType.isPresent());
    assertEquals(flushType.get(), BufferFlushType.FLUSH_SINGLE_STREAM);

    // The buffer limit is now reached for stream2, flushing that single stream only
    verify(perStreamFlushHook, times(0)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(1)).accept(stream2, recordWriter2);

    when(recordWriter2.getByteCount()).thenReturn(10L); // back to one record in recordWriter2
    assertFalse(buffering.addRecord(stream2, message5).isPresent());

    // force flush to terminate test
    buffering.flushAll();
    verify(perStreamFlushHook, times(1)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(2)).accept(stream2, recordWriter2);
  }

  @Test
  public void testTotalStreamThresholdFlush() throws Exception {
    final SerializedBufferingStrategy buffering = new SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook);
    final AirbyteStreamNameNamespacePair stream1 = new AirbyteStreamNameNamespacePair(STREAM_1, "namespace");
    final AirbyteStreamNameNamespacePair stream2 = new AirbyteStreamNameNamespacePair(STREAM_2, "namespace");
    final AirbyteStreamNameNamespacePair stream3 = new AirbyteStreamNameNamespacePair(STREAM_3, "namespace");
    // To test total stream threshold, we are sending test messages to multiple streams without reaching
    // per stream limits
    final AirbyteMessage message1 = generateMessage(stream1);
    final AirbyteMessage message2 = generateMessage(stream2);
    final AirbyteMessage message3 = generateMessage(stream3);
    final AirbyteMessage message4 = generateMessage(stream1);
    final AirbyteMessage message5 = generateMessage(stream2);
    final AirbyteMessage message6 = generateMessage(stream3);

    assertFalse(buffering.addRecord(stream1, message1).isPresent());
    assertFalse(buffering.addRecord(stream2, message2).isPresent());
    // Total and per stream Buffers still have room
    verify(perStreamFlushHook, times(0)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(0)).accept(stream2, recordWriter2);
    verify(perStreamFlushHook, times(0)).accept(stream3, recordWriter3);

    assertFalse(buffering.addRecord(stream3, message3).isPresent());
    when(recordWriter1.getByteCount()).thenReturn(20L); // second record in recordWriter1
    assertFalse(buffering.addRecord(stream1, message4).isPresent());
    when(recordWriter2.getByteCount()).thenReturn(20L); // second record in recordWriter2

    // In response to checkpointing, will need to know what type of buffer flush occurred to mark
    // AirbyteStateMessage as committed depending on DestDefaultStateLifecycleManager
    final Optional<BufferFlushType> flushType = buffering.addRecord(stream2, message5);
    assertTrue(flushType.isPresent());
    assertEquals(flushType.get(), BufferFlushType.FLUSH_ALL);

    // Buffer limit reached for total streams, flushing all streams
    verify(perStreamFlushHook, times(1)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(1)).accept(stream2, recordWriter2);
    verify(perStreamFlushHook, times(1)).accept(stream3, recordWriter3);

    assertFalse(buffering.addRecord(stream3, message6).isPresent());
    // force flush to terminate test
    buffering.flushAll();
    verify(perStreamFlushHook, times(1)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(1)).accept(stream2, recordWriter2);
    verify(perStreamFlushHook, times(2)).accept(stream3, recordWriter3);
  }

  @Test
  public void testConcurrentStreamThresholdFlush() throws Exception {
    final SerializedBufferingStrategy buffering = new SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook);
    final AirbyteStreamNameNamespacePair stream1 = new AirbyteStreamNameNamespacePair(STREAM_1, "namespace1");
    final AirbyteStreamNameNamespacePair stream2 = new AirbyteStreamNameNamespacePair(STREAM_2, "namespace2");
    final AirbyteStreamNameNamespacePair stream3 = new AirbyteStreamNameNamespacePair(STREAM_3, null);
    final AirbyteStreamNameNamespacePair stream4 = new AirbyteStreamNameNamespacePair(STREAM_4, null);
    // To test concurrent stream threshold, we are sending test messages to multiple streams
    final AirbyteMessage message1 = generateMessage(stream1);
    final AirbyteMessage message2 = generateMessage(stream2);
    final AirbyteMessage message3 = generateMessage(stream3);
    final AirbyteMessage message4 = generateMessage(stream4);
    final AirbyteMessage message5 = generateMessage(stream1);

    assertFalse(buffering.addRecord(stream1, message1).isPresent());
    assertFalse(buffering.addRecord(stream2, message2).isPresent());
    assertFalse(buffering.addRecord(stream3, message3).isPresent());
    // Total and per stream Buffers still have room
    verify(perStreamFlushHook, times(0)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(0)).accept(stream2, recordWriter2);
    verify(perStreamFlushHook, times(0)).accept(stream3, recordWriter3);

    // Since the concurrent stream threshold has been exceeded, all buffer streams are flush
    final Optional<BufferFlushType> flushType = buffering.addRecord(stream4, message4);
    assertTrue(flushType.isPresent());
    assertEquals(flushType.get(), BufferFlushType.FLUSH_ALL);

    // Buffer limit reached for concurrent streams, flushing all streams
    verify(perStreamFlushHook, times(1)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(1)).accept(stream2, recordWriter2);
    verify(perStreamFlushHook, times(1)).accept(stream3, recordWriter3);
    verify(perStreamFlushHook, times(1)).accept(stream4, recordWriter4);

    assertFalse(buffering.addRecord(stream1, message5).isPresent());
    // force flush to terminate test
    buffering.flushAll();
    verify(perStreamFlushHook, times(2)).accept(stream1, recordWriter1);
    verify(perStreamFlushHook, times(1)).accept(stream2, recordWriter2);
    verify(perStreamFlushHook, times(1)).accept(stream3, recordWriter3);
    verify(perStreamFlushHook, times(1)).accept(stream4, recordWriter4);
  }

  @Test
  public void testCreateBufferFailure() {
    final SerializedBufferingStrategy buffering = new SerializedBufferingStrategy(onCreateBufferFunction(), catalog, perStreamFlushHook);
    final AirbyteStreamNameNamespacePair stream = new AirbyteStreamNameNamespacePair("unknown_stream", "namespace1");
    assertThrows(RuntimeException.class, () -> buffering.addRecord(stream, generateMessage(stream)));
  }

  private static AirbyteMessage generateMessage(final AirbyteStreamNameNamespacePair stream) {
    return new AirbyteMessage().withRecord(new AirbyteRecordMessage()
        .withStream(stream.getName())
        .withNamespace(stream.getNamespace())
        .withData(MESSAGE_DATA));
  }

  private CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBufferFunction() {
    return (stream, catalog) -> switch (stream.getName()) {
      case STREAM_1 -> recordWriter1;
      case STREAM_2 -> recordWriter2;
      case STREAM_3 -> recordWriter3;
      case STREAM_4 -> recordWriter4;
      default -> null;
    };
  }

}
