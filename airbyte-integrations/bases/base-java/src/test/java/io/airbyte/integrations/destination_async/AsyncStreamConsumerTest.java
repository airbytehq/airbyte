/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteRecordMessage;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.io.IOException;
import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.apache.commons.lang.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class AsyncStreamConsumerTest {

  private static final int RECORD_SIZE_20_BYTES = 20;

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = STREAM_NAME + 2;
  private static final StreamDescriptor STREAM1_DESC = new StreamDescriptor()
      .withNamespace(SCHEMA_NAME)
      .withName(STREAM_NAME);

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
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(STREAM1_DESC).withStreamState(Jsons.jsonNode(1))));
  private static final AirbyteMessage STATE_MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(STREAM1_DESC).withStreamState(Jsons.jsonNode(2))));

  private AsyncStreamConsumer consumer;
  private OnStartFunction onStart;
  private DestinationFlushFunction flushFunction;
  private OnCloseFunction onClose;
  private Consumer<AirbyteMessage> outputRecordCollector;
  private FlushFailure flushFailure;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() {
    onStart = mock(OnStartFunction.class);
    onClose = mock(OnCloseFunction.class);
    flushFunction = mock(DestinationFlushFunction.class);
    outputRecordCollector = mock(Consumer.class);
    flushFailure = mock(FlushFailure.class);
    consumer = new AsyncStreamConsumer(
        outputRecordCollector,
        onStart,
        onClose,
        flushFunction,
        CATALOG,
        new BufferManager(),
        flushFailure);

    when(flushFunction.getOptimalBatchSizeBytes()).thenReturn(10_000L);
  }

  @Test
  void test1StreamWith1State() throws Exception {
    final List<PartialAirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(Jsons.serialize(STATE_MESSAGE1), RECORD_SIZE_20_BYTES);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector).accept(STATE_MESSAGE1);
  }

  @Test
  void test1StreamWith2State() throws Exception {
    final List<PartialAirbyteMessage> expectedRecords = generateRecords(1_000);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(Jsons.serialize(STATE_MESSAGE1), RECORD_SIZE_20_BYTES);
    consumer.accept(Jsons.serialize(STATE_MESSAGE2), RECORD_SIZE_20_BYTES);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(outputRecordCollector, times(1)).accept(STATE_MESSAGE2);
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
  void testShouldBlockWhenQueuesAreFull() throws Exception {
    consumer.start();

  }

  /*
   * Tests that the consumer will block when the buffer is full. Achieves this by setting optimal
   * batch size to 0, so the flush worker never actually pulls anything from the queue.
   */
  @Test
  void testBackPressure() throws Exception {
    flushFunction = mock(DestinationFlushFunction.class);
    flushFailure = mock(FlushFailure.class);
    consumer = new AsyncStreamConsumer(
        m -> {},
        () -> {},
        () -> {},
        flushFunction,
        CATALOG,
        new BufferManager(1024 * 10),
        flushFailure);
    when(flushFunction.getOptimalBatchSizeBytes()).thenReturn(0L);

    final AtomicLong recordCount = new AtomicLong();

    consumer.start();

    final ExecutorService executor = Executors.newSingleThreadExecutor();
    while (true) {
      final Future<?> future = executor.submit(() -> {
        try {
          consumer.accept(Jsons.serialize(new AirbyteMessage()
              .withType(Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(STREAM_NAME)
                  .withNamespace(SCHEMA_NAME)
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(Jsons.jsonNode(recordCount.getAndIncrement())))),
              RECORD_SIZE_20_BYTES);
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      });

      try {
        future.get(1, TimeUnit.SECONDS);
      } catch (final TimeoutException e) {
        future.cancel(true); // Stop the operation running in thread
        break;
      }
    }
    executor.shutdownNow();

    assertTrue(recordCount.get() < 1000, String.format("Record count was %s", recordCount.get()));
  }

  @Nested
  class ErrorHandling {

    @Test
    void testErrorOnAccept() throws Exception {
      when(flushFailure.isFailed()).thenReturn(false).thenReturn(true);
      when(flushFailure.getException()).thenReturn(new IOException("test exception"));

      final var m = new AirbyteMessage()
          .withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream(STREAM_NAME)
              .withNamespace(SCHEMA_NAME)
              .withEmittedAt(Instant.now().toEpochMilli())
              .withData(Jsons.deserialize("")));
      consumer.start();
      consumer.accept(Jsons.serialize(m), RECORD_SIZE_20_BYTES);
      assertThrows(IOException.class, () -> consumer.accept(Jsons.serialize(m), RECORD_SIZE_20_BYTES));
    }

    @Test
    void testErrorOnClose() throws Exception {
      when(flushFailure.isFailed()).thenReturn(true);
      when(flushFailure.getException()).thenReturn(new IOException("test exception"));

      consumer.start();
      assertThrows(IOException.class, () -> consumer.close());
    }

  }

  private static void consumeRecords(final AsyncStreamConsumer consumer, final Collection<PartialAirbyteMessage> records) {
    records.forEach(m -> {
      try {
        consumer.accept(m.getSerialized(), RECORD_SIZE_20_BYTES);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  // NOTE: Generates records at chunks of 160 bytes
  @SuppressWarnings("SameParameterValue")
  private static List<PartialAirbyteMessage> generateRecords(final long targetSizeInBytes) {
    final List<PartialAirbyteMessage> output = Lists.newArrayList();
    long bytesCounter = 0;
    for (int i = 0;; i++) {
      final JsonNode payload =
          Jsons.jsonNode(ImmutableMap.of("id", RandomStringUtils.randomAlphabetic(7), "name", "human " + String.format("%8d", i)));
      final long sizeInBytes = RecordSizeEstimator.getStringByteSize(payload);
      bytesCounter += sizeInBytes;
      final PartialAirbyteMessage airbyteMessage = new PartialAirbyteMessage()
          .withType(Type.RECORD)
          .withRecord(new PartialAirbyteRecordMessage()
              .withStream(STREAM_NAME)
              .withNamespace(SCHEMA_NAME))
          .withSerialized(Jsons.serialize(new AirbyteMessage()
              .withType(Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(STREAM_NAME)
                  .withNamespace(SCHEMA_NAME)
                  .withData(payload))));
      if (bytesCounter > targetSizeInBytes) {
        break;
      } else {
        output.add(airbyteMessage);
      }
    }
    return output;
  }

  private void verifyStartAndClose() throws Exception {
    verify(onStart).call();
    verify(onClose).call();
  }

  @SuppressWarnings({"unchecked", "SameParameterValue"})
  private void verifyRecords(final String streamName, final String namespace, final Collection<PartialAirbyteMessage> expectedRecords)
      throws Exception {
    final ArgumentCaptor<Stream<PartialAirbyteMessage>> argumentCaptor = ArgumentCaptor.forClass(Stream.class);
    verify(flushFunction, atLeast(1)).flush(
        eq(new StreamDescriptor().withNamespace(namespace).withName(streamName)),
        argumentCaptor.capture());

    // captures the output of all the workers, since our records could come out in any of them.
    final List<PartialAirbyteMessage> actualRecords = argumentCaptor
        .getAllValues()
        .stream()
        // flatten those results into a single list for the simplicity of comparison
        .flatMap(s -> s)
        .toList();
    assertEquals(expectedRecords.stream().toList(), actualRecords);
  }

}
