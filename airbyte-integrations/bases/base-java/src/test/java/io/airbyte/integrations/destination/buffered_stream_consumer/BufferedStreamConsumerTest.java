/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.record_buffer.InMemoryRecordBufferingStrategy;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Duration;
import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class BufferedStreamConsumerTest {

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = STREAM_NAME + 2;
  private static final int PERIODIC_BUFFER_FREQUENCY = 5;
  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING)),
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME2,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING))));

  private static final AirbyteMessage STATE_MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 1))));
  private static final AirbyteMessage STATE_MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 2))));

  private BufferedStreamConsumer consumer;
  private OnStartFunction onStart;
  private RecordWriter<AirbyteRecordMessage> recordWriter;
  private OnCloseFunction onClose;
  private CheckedFunction<JsonNode, Boolean, Exception> isValidRecord;
  private Consumer<AirbyteMessage> outputRecordCollector;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws Exception {
    onStart = mock(OnStartFunction.class);
    recordWriter = mock(RecordWriter.class);
    onClose = mock(OnCloseFunction.class);
    isValidRecord = mock(CheckedFunction.class);
    outputRecordCollector = mock(Consumer.class);
    consumer = new BufferedStreamConsumer(
        outputRecordCollector,
        onStart,
        new InMemoryRecordBufferingStrategy(recordWriter, 1_000),
        onClose,
        CATALOG,
        isValidRecord);

    when(isValidRecord.apply(any())).thenReturn(true);
  }

  @Test
  void test1StreamWith1State() throws Exception {
    final List<AirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(STATE_MESSAGE1);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void test1StreamWith2State() throws Exception {
    final List<AirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(STATE_MESSAGE1);
    consumer.accept(STATE_MESSAGE2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector, times(1)).accept(STATE_MESSAGE2);
  }

  @Test
  void test1StreamWith0State() throws Exception {
    final List<AirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);
  }

  @Test
  void test1StreamWithStateAndThenMoreRecordsBiggerThanBuffer() throws Exception {
    final List<AirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);
    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch2);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void test1StreamWithStateAndThenMoreRecordsSmallerThanBuffer() throws Exception {
    final List<AirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);

    // consumer with big enough buffered that we see both batches are flushed in one go.
    final BufferedStreamConsumer consumer = new BufferedStreamConsumer(
        outputRecordCollector,
        onStart,
        new InMemoryRecordBufferingStrategy(recordWriter, 10_000),
        onClose,
        CATALOG,
        isValidRecord);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    consumer.close();

    verifyStartAndClose();

    final List<AirbyteMessage> expectedRecords = Lists.newArrayList(expectedRecordsBatch1, expectedRecordsBatch2)
        .stream()
        .flatMap(Collection::stream)
        .collect(Collectors.toList());
    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void testExceptionAfterOneStateMessage() throws Exception {
    final List<AirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch3 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    when(isValidRecord.apply(any())).thenThrow(new IllegalStateException("induced exception"));
    assertThrows(IllegalStateException.class, () -> consumer.accept(expectedRecordsBatch3.get(0)));
    consumer.close();

    verifyStartAndCloseFailure();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void testExceptionAfterNoStateMessages() throws Exception {
    final List<AirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch3 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumeRecords(consumer, expectedRecordsBatch2);
    when(isValidRecord.apply(any())).thenThrow(new IllegalStateException("induced exception"));
    assertThrows(IllegalStateException.class, () -> consumer.accept(expectedRecordsBatch3.get(0)));
    consumer.close();

    verifyStartAndCloseFailure();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);

    verifyNoInteractions(outputRecordCollector);
  }

  @Test
  void testExceptionDuringOnClose() throws Exception {
    doThrow(new IllegalStateException("induced exception")).when(onClose).accept(false);

    final List<AirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    assertThrows(IllegalStateException.class, () -> consumer.close(), "Expected an error to be thrown on close");

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void test2StreamWith1State() throws Exception {
    final List<AirbyteMessage> expectedRecordsStream1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsStream2 = expectedRecordsStream1
        .stream()
        .map(Jsons::clone)
        .peek(m -> m.getRecord().withStream(STREAM_NAME2))
        .collect(Collectors.toList());

    consumer.start();
    consumeRecords(consumer, expectedRecordsStream1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsStream2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsStream1);
    verifyRecords(STREAM_NAME2, SCHEMA_NAME, expectedRecordsStream2);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void test2StreamWith2State() throws Exception {
    final List<AirbyteMessage> expectedRecordsStream1 = generateRecords(1_000);
    final List<AirbyteMessage> expectedRecordsStream2 = expectedRecordsStream1
        .stream()
        .map(Jsons::clone)
        .peek(m -> m.getRecord().withStream(STREAM_NAME2))
        .collect(Collectors.toList());

    consumer.start();
    consumeRecords(consumer, expectedRecordsStream1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsStream2);
    consumer.accept(STATE_MESSAGE2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsStream1);
    verifyRecords(STREAM_NAME2, SCHEMA_NAME, expectedRecordsStream2);

    verify(outputRecordCollector, times(1)).accept(STATE_MESSAGE2);
  }

  // Periodic Buffer Flush Tests
  @Test
  void testSlowStreamReturnsState() throws Exception {
    // generate records less than the default maxQueueSizeInBytes to confirm periodic flushing occurs
    final List<AirbyteMessage> expectedRecordsStream1 = generateRecords(500L);
    final List<AirbyteMessage> expectedRecordsStream1Batch2 = generateRecords(200L);

    // Overrides flush frequency for testing purposes to 5 seconds
    final BufferedStreamConsumer flushConsumer = getConsumerWithFlushFrequency();
    flushConsumer.start();
    consumeRecords(flushConsumer, expectedRecordsStream1);
    flushConsumer.accept(STATE_MESSAGE1);
    // NOTE: Sleeps process for 5 seconds, if tests are slow this can be updated to reduce slowdowns
    TimeUnit.SECONDS.sleep(PERIODIC_BUFFER_FREQUENCY);
    consumeRecords(flushConsumer, expectedRecordsStream1Batch2);
    flushConsumer.close();

    verifyStartAndClose();
    // expects the records to be grouped because periodicBufferFlush occurs at the end of acceptTracked
    verifyRecords(STREAM_NAME, SCHEMA_NAME,
        Stream.concat(expectedRecordsStream1.stream(), expectedRecordsStream1Batch2.stream()).collect(Collectors.toList()));
    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void testSlowStreamReturnsMultipleStates() throws Exception {
    // generate records less than the default maxQueueSizeInBytes to confirm periodic flushing occurs
    final List<AirbyteMessage> expectedRecordsStream1 = generateRecords(500L);
    final List<AirbyteMessage> expectedRecordsStream1Batch2 = generateRecords(200L);
    // creates records equal to size that triggers buffer flush
    final List<AirbyteMessage> expectedRecordsStream1Batch3 = generateRecords(1_000L);

    // Overrides flush frequency for testing purposes to 5 seconds
    final BufferedStreamConsumer flushConsumer = getConsumerWithFlushFrequency();
    flushConsumer.start();
    consumeRecords(flushConsumer, expectedRecordsStream1);
    flushConsumer.accept(STATE_MESSAGE1);
    // NOTE: Sleeps process for 5 seconds, if tests are slow this can be updated to reduce slowdowns
    TimeUnit.SECONDS.sleep(PERIODIC_BUFFER_FREQUENCY);
    consumeRecords(flushConsumer, expectedRecordsStream1Batch2);
    consumeRecords(flushConsumer, expectedRecordsStream1Batch3);
    flushConsumer.accept(STATE_MESSAGE2);
    flushConsumer.close();

    verifyStartAndClose();
    // expects the records to be grouped because periodicBufferFlush occurs at the end of acceptTracked
    verifyRecords(STREAM_NAME, SCHEMA_NAME,
        Stream.concat(expectedRecordsStream1.stream(), expectedRecordsStream1Batch2.stream()).collect(Collectors.toList()));
    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsStream1Batch3);
    // expects two STATE messages returned since one will be flushed after periodic flushing occurs
    // and the other after buffer has been filled
    verify(outputRecordCollector).accept(STATE_MESSAGE1);
    verify(outputRecordCollector).accept(STATE_MESSAGE2);
  }

  private BufferedStreamConsumer getConsumerWithFlushFrequency() {
    final BufferedStreamConsumer flushFrequencyConsumer = new BufferedStreamConsumer(
        outputRecordCollector,
        onStart,
        new InMemoryRecordBufferingStrategy(recordWriter, 10_000),
        onClose,
        CATALOG,
        isValidRecord,
        Duration.ofSeconds(PERIODIC_BUFFER_FREQUENCY));
    return flushFrequencyConsumer;
  }

  private void verifyStartAndClose() throws Exception {
    verify(onStart).call();
    verify(onClose).accept(false);
  }

  /** Indicates that a failure occurred while consuming AirbyteMessages */
  private void verifyStartAndCloseFailure() throws Exception {
    verify(onStart).call();
    verify(onClose).accept(true);
  }

  private static void consumeRecords(final BufferedStreamConsumer consumer, final Collection<AirbyteMessage> records) {
    records.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  // NOTE: Generates records at chunks of 160 bytes
  private static List<AirbyteMessage> generateRecords(final long targetSizeInBytes) {
    final List<AirbyteMessage> output = Lists.newArrayList();
    long bytesCounter = 0;
    for (int i = 0;; i++) {
      final JsonNode payload =
          Jsons.jsonNode(ImmutableMap.of("id", RandomStringUtils.randomAlphabetic(7), "name", "human " + String.format("%8d", i)));
      final long sizeInBytes = RecordSizeEstimator.getStringByteSize(payload);
      bytesCounter += sizeInBytes;
      final AirbyteMessage airbyteMessage = new AirbyteMessage()
          .withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream(STREAM_NAME)
              .withNamespace(SCHEMA_NAME)
              .withEmittedAt(Instant.now().toEpochMilli())
              .withData(payload));
      if (bytesCounter > targetSizeInBytes) {
        break;
      } else {
        output.add(airbyteMessage);
      }
    }
    return output;
  }

  private void verifyRecords(final String streamName, final String namespace, final Collection<AirbyteMessage> expectedRecords) throws Exception {
    verify(recordWriter).accept(
        new AirbyteStreamNameNamespacePair(streamName, namespace),
        expectedRecords.stream().map(AirbyteMessage::getRecord).collect(Collectors.toList()));
  }

}
