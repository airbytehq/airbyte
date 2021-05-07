/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.time.Instant;
import java.util.Collection;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class BufferedStreamConsumerTest {

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = STREAM_NAME + 2;
  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaPrimitive.NUMBER),
          Field.of("name", JsonSchemaPrimitive.STRING)),
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME2,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaPrimitive.NUMBER),
          Field.of("name", JsonSchemaPrimitive.STRING))));

  private static final AirbyteMessage STATE_MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 1))));
  private static final AirbyteMessage STATE_MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("state_message_id", 2))));

  private BufferedStreamConsumer consumer;
  private VoidCallable onStart;
  private RecordWriter recordWriter;
  private CheckedConsumer<Boolean, Exception> onClose;
  private CheckedFunction<String, Boolean, Exception> isValidRecord;
  private Consumer<AirbyteMessage> checkpointConsumer;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws Exception {
    onStart = mock(VoidCallable.class);
    recordWriter = mock(RecordWriter.class);
    onClose = mock(CheckedConsumer.class);
    isValidRecord = mock(CheckedFunction.class);
    checkpointConsumer = mock(Consumer.class);
    consumer = new BufferedStreamConsumer(
        checkpointConsumer,
        onStart,
        recordWriter,
        onClose,
        CATALOG,
        isValidRecord);

    when(isValidRecord.apply(any())).thenReturn(true);
  }

  @Test
  void test1StreamWith1State() throws Exception {
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(STATE_MESSAGE1);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(checkpointConsumer).accept(STATE_MESSAGE1);
  }

  @Test
  void test1StreamWith2State() throws Exception {
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.accept(STATE_MESSAGE1);
    consumer.accept(STATE_MESSAGE2);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);

    verify(checkpointConsumer, times(1)).accept(STATE_MESSAGE2);
  }

  @Test
  void test1StreamWith0State() throws Exception {
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();
    consumeRecords(consumer, expectedRecords);
    consumer.close();

    verifyStartAndClose();

    verifyRecords(STREAM_NAME, SCHEMA_NAME, expectedRecords);
  }

  @Test
  void test1StreamWithStateAndThenMoreRecords() throws Exception {
    final List<AirbyteMessage> expectedRecordsBatch1 = getNRecords(10);
    final List<AirbyteMessage> expectedRecordsBatch2 = getNRecords(10, 20);

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

    verify(checkpointConsumer).accept(STATE_MESSAGE1);
  }

  @Test
  void test2StreamWith1State() throws Exception {
    final List<AirbyteMessage> expectedRecordsStream1 = getNRecords(10);
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

    verify(checkpointConsumer).accept(STATE_MESSAGE1);
  }

  @Test
  void test2StreamWith2State() throws Exception {
    final List<AirbyteMessage> expectedRecordsStream1 = getNRecords(10);
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

    verify(checkpointConsumer, times(1)).accept(STATE_MESSAGE2);
  }

  private void verifyStartAndClose() throws Exception {
    verify(onStart).call();
    verify(onClose).accept(false);
  }

  private static void consumeRecords(BufferedStreamConsumer consumer, Collection<AirbyteMessage> records) {
    records.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  private static List<AirbyteMessage> getNRecords(int endExclusive) {
    return getNRecords(0, endExclusive);
  }

  private static List<AirbyteMessage> getNRecords(int startInclusive, int endExclusive) {
    return IntStream.range(startInclusive, endExclusive)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(SCHEMA_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());
  }

  private void verifyRecords(String streamName, String namespace, Collection<AirbyteMessage> expectedRecords) throws Exception {
    verify(recordWriter).accept(
        new AirbyteStreamNameNamespacePair(streamName, namespace),
        expectedRecords.stream().map(AirbyteMessage::getRecord).collect(Collectors.toList()));
  }

}
