/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.destination.record_buffer.BufferFlushType;
import io.airbyte.cdk.integrations.destination.record_buffer.BufferingStrategy;
import io.airbyte.cdk.integrations.destination.record_buffer.InMemoryRecordBufferingStrategy;
import io.airbyte.cdk.protocol.PartialAirbyteGlobalState;
import io.airbyte.cdk.protocol.PartialAirbyteMessage;
import io.airbyte.cdk.protocol.PartialAirbyteRecordMessage;
import io.airbyte.cdk.protocol.PartialAirbyteStateMessage;
import io.airbyte.cdk.protocol.PartialAirbyteStreamState;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Duration;
import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
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

  private static final PartialAirbyteMessage STATE_MESSAGE1 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 1))));
  private static final PartialAirbyteMessage STATE_MESSAGE2 = new PartialAirbyteMessage()
      .withType(Type.STATE)
      .withState(new PartialAirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 2))));

  private BufferedStreamConsumer consumer;
  private OnStartFunction onStart;
  private RecordWriter<PartialAirbyteRecordMessage> recordWriter;
  private OnCloseFunction onClose;
  private CheckedFunction<String, Boolean, Exception> isValidRecord;
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
    final List<PartialAirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(STATE_MESSAGE1);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void test1StreamWith2State() throws Exception {
    final List<PartialAirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(STATE_MESSAGE1);
    consumer.accept(STATE_MESSAGE2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector, times(1)).accept(STATE_MESSAGE2.toFullMessage());
  }

  @Test
  void test1StreamWith0State() throws Exception {
    final List<PartialAirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);
  }

  @Test
  void test1StreamWithStateAndThenMoreRecordsBiggerThanBuffer() throws Exception {
    final List<PartialAirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);
    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch2);

    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void test1StreamWithStateAndThenMoreRecordsSmallerThanBuffer() throws Exception {
    final List<PartialAirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);

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

    final List<PartialAirbyteMessage> expectedRecords = Lists.newArrayList(expectedRecordsBatch1, expectedRecordsBatch2)
        .stream()
        .flatMap(Collection::stream)
        .collect(Collectors.toList());
    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void testExceptionAfterOneStateMessage() throws Exception {
    final List<PartialAirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch3 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    when(isValidRecord.apply(any())).thenThrow(new IllegalStateException("induced exception"));
    assertThrows(IllegalStateException.class, () -> consumer.accept(expectedRecordsBatch3.get(0)));
    consumer.close();

    verifyStartAndCloseFailure();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);

    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void testExceptionAfterNoStateMessages() throws Exception {
    final List<PartialAirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch3 = generateRecords(1_000);

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

    final List<PartialAirbyteMessage> expectedRecordsBatch1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsBatch2 = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecordsBatch1);
    consumer.accept(STATE_MESSAGE1);
    consumeRecords(consumer, expectedRecordsBatch2);
    assertThrows(IllegalStateException.class, () -> consumer.close(), "Expected an error to be thrown on close");

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecordsBatch1);

    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void test2StreamWith1State() throws Exception {
    final List<PartialAirbyteMessage> expectedRecordsStream1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsStream2 = expectedRecordsStream1
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

    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void test2StreamWith2State() throws Exception {
    final List<PartialAirbyteMessage> expectedRecordsStream1 = generateRecords(1_000);
    final List<PartialAirbyteMessage> expectedRecordsStream2 = expectedRecordsStream1
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

    verify(outputRecordCollector, times(1)).accept(STATE_MESSAGE2.toFullMessage());
  }

  // Periodic Buffer Flush Tests
  @Test
  void testSlowStreamReturnsState() throws Exception {
    // generate records less than the default maxQueueSizeInBytes to confirm periodic flushing occurs
    final List<PartialAirbyteMessage> expectedRecordsStream1 = generateRecords(500L);
    final List<PartialAirbyteMessage> expectedRecordsStream1Batch2 = generateRecords(200L);

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
    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
  }

  @Test
  void testSlowStreamReturnsMultipleStates() throws Exception {
    // generate records less than the default maxQueueSizeInBytes to confirm periodic flushing occurs
    final List<PartialAirbyteMessage> expectedRecordsStream1 = generateRecords(500L);
    final List<PartialAirbyteMessage> expectedRecordsStream1Batch2 = generateRecords(200L);
    // creates records equal to size that triggers buffer flush
    final List<PartialAirbyteMessage> expectedRecordsStream1Batch3 = generateRecords(1_000L);

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
    verify(outputRecordCollector).accept(STATE_MESSAGE1.toFullMessage());
    verify(outputRecordCollector).accept(STATE_MESSAGE2.toFullMessage());
  }

  /**
   * Verify that if we ack a state message for stream2 while stream1 has unflushed records+state, that
   * we do _not_ ack stream1's state message.
   */
  @Test
  void testStreamTail() throws Exception {
    // InMemoryRecordBufferingStrategy always returns FLUSH_ALL, so just mock a new strategy here
    final BufferingStrategy strategy = mock(BufferingStrategy.class);
    // The first two records that we push will not trigger any flushes, but the third record _will_
    // trigger a flush
    when(strategy.addRecord(any(), any())).thenReturn(
        Optional.empty(),
        Optional.empty(),
        Optional.of(BufferFlushType.FLUSH_SINGLE_STREAM));
    consumer = new BufferedStreamConsumer(
        outputRecordCollector,
        onStart,
        strategy,
        onClose,
        CATALOG,
        isValidRecord,
        // Never periodic flush
        Duration.ofHours(24),
        null);
    final List<PartialAirbyteMessage> expectedRecordsStream1 = List.of(new PartialAirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream(STREAM_NAME)
            .withNamespace(SCHEMA_NAME)));
    final List<PartialAirbyteMessage> expectedRecordsStream2 = List.of(new PartialAirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream(STREAM_NAME2)
            .withNamespace(SCHEMA_NAME)));

    final PartialAirbyteMessage state1 = new PartialAirbyteMessage()
        .withType(Type.STATE)
        .withState(new PartialAirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new PartialAirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME).withNamespace(SCHEMA_NAME))
                .withStreamState(Jsons.jsonNode(ImmutableMap.of("state_message_id", 1)))));
    final PartialAirbyteMessage state2 = new PartialAirbyteMessage()
        .withType(Type.STATE)
        .withState(new PartialAirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new PartialAirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME2).withNamespace(SCHEMA_NAME))
                .withStreamState(Jsons.jsonNode(ImmutableMap.of("state_message_id", 2)))));

    consumer.start();
    consumeRecords(consumer, expectedRecordsStream1);
    consumer.accept(state1);
    // At this point, we have not yet flushed anything
    consumeRecords(consumer, expectedRecordsStream2);
    consumer.accept(state2);
    consumeRecords(consumer, expectedRecordsStream2);
    // Now we have flushed stream 2, but not stream 1
    // Verify that we have only acked stream 2's state.
    verify(outputRecordCollector).accept(state2.toFullMessage());
    verify(outputRecordCollector, never()).accept(state1.toFullMessage());

    consumer.close();
    // Now we've closed the consumer, which flushes everything.
    // Verify that we ack stream 1's pending state.
    verify(outputRecordCollector).accept(state1.toFullMessage());
  }

  /**
   * Same idea as {@link #testStreamTail()} but with global state. We shouldn't emit any state
   * messages until we close the consumer.
   */
  @Test
  void testStreamTailGlobalState() throws Exception {
    // InMemoryRecordBufferingStrategy always returns FLUSH_ALL, so just mock a new strategy here
    final BufferingStrategy strategy = mock(BufferingStrategy.class);
    // The first two records that we push will not trigger any flushes, but the third record _will_
    // trigger a flush
    when(strategy.addRecord(any(), any())).thenReturn(
        Optional.empty(),
        Optional.empty(),
        Optional.of(BufferFlushType.FLUSH_SINGLE_STREAM));
    consumer = new BufferedStreamConsumer(
        outputRecordCollector,
        onStart,
        strategy,
        onClose,
        CATALOG,
        isValidRecord,
        // Never periodic flush
        Duration.ofHours(24),
        null);
    final List<PartialAirbyteMessage> expectedRecordsStream1 = List.of(new PartialAirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream(STREAM_NAME)
            .withNamespace(SCHEMA_NAME)));
    final List<PartialAirbyteMessage> expectedRecordsStream2 = List.of(new PartialAirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new PartialAirbyteRecordMessage()
            .withStream(STREAM_NAME2)
            .withNamespace(SCHEMA_NAME)));

    final PartialAirbyteMessage state1 = new PartialAirbyteMessage()
        .withType(Type.STATE)
        .withState(new PartialAirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
            .withGlobal(new PartialAirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(ImmutableMap.of("state_message_id", 1)))));
    final PartialAirbyteMessage state2 = new PartialAirbyteMessage()
        .withType(Type.STATE)
        .withState(new PartialAirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
            .withGlobal(new PartialAirbyteGlobalState()
                .withSharedState(Jsons.jsonNode(ImmutableMap.of("state_message_id", 2)))));

    consumer.start();
    consumeRecords(consumer, expectedRecordsStream1);
    consumer.accept(state1);
    // At this point, we have not yet flushed anything
    consumeRecords(consumer, expectedRecordsStream2);
    consumer.accept(state2);
    consumeRecords(consumer, expectedRecordsStream2);
    // Now we have flushed stream 2, but not stream 1
    // We should not have acked any state yet, because we haven't written stream1's records yet.
    verify(outputRecordCollector, never()).accept(any());

    consumer.close();
    // Now we've closed the consumer, which flushes everything.
    // Verify that we ack the final state.
    // Note that we discard state1 entirely - this is OK. As long as we ack the last state message,
    // the source can correctly resume from that point.
    verify(outputRecordCollector).accept(state2.toFullMessage());
  }

  private BufferedStreamConsumer getConsumerWithFlushFrequency() {
    final BufferedStreamConsumer flushFrequencyConsumer = new BufferedStreamConsumer(
        outputRecordCollector,
        onStart,
        new InMemoryRecordBufferingStrategy(recordWriter, 10_000),
        onClose,
        CATALOG,
        isValidRecord,
        Duration.ofSeconds(PERIODIC_BUFFER_FREQUENCY),
        null);
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

  private static void consumeRecords(final BufferedStreamConsumer consumer, final Collection<PartialAirbyteMessage> records) {
    records.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  // NOTE: Generates records at chunks of 160 bytes
  private static List<PartialAirbyteMessage> generateRecords(final long targetSizeInBytes) {
    final List<PartialAirbyteMessage> output = Lists.newArrayList();
    long bytesCounter = 0;
    for (int i = 0;; i++) {
      final JsonNode payload =
          Jsons.jsonNode(ImmutableMap.of("id", RandomStringUtils.randomAlphabetic(7), "name", "human " + String.format("%8d", i)));
      final long sizeInBytes = RecordSizeEstimator.getStringByteSize(Jsons.serialize(payload));
      bytesCounter += sizeInBytes;
      final PartialAirbyteMessage airbyteMessage = new PartialAirbyteMessage()
          .withType(Type.RECORD)
          .withRecord(new PartialAirbyteRecordMessage()
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

  private void verifyRecords(final String streamName, final String namespace, final Collection<PartialAirbyteMessage> expectedRecords)
      throws Exception {
    verify(recordWriter).accept(
        new AirbyteStreamNameNamespacePair(streamName, namespace),
        expectedRecords.stream().map(PartialAirbyteMessage::getRecord).collect(Collectors.toList()));
  }

}
