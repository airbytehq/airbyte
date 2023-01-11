/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.MdcScope.Builder;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;

class DefaultAirbyteStreamFactoryTest {

  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private AirbyteProtocolPredicate protocolPredicate;
  private Logger logger;

  @BeforeEach
  void setup() {
    protocolPredicate = mock(AirbyteProtocolPredicate.class);
    when(protocolPredicate.test(any())).thenReturn(true);
    logger = mock(Logger.class);
  }

  @Test
  void testValid() {
    final AirbyteMessage record1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green");

    final Stream<AirbyteMessage> messageStream = stringToMessageStream(Jsons.serialize(record1));
    final Stream<AirbyteMessage> expectedStream = Stream.of(record1);

    assertEquals(expectedStream.collect(Collectors.toList()), messageStream.collect(Collectors.toList()));
    verifyNoInteractions(logger);
  }

  @Test
  void testLoggingLine() {
    final String invalidRecord = "invalid line";

    final Stream<AirbyteMessage> messageStream = stringToMessageStream(invalidRecord);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).info(anyString());
    verifyNoMoreInteractions(logger);
  }

  @Test
  void testLoggingLevel() {
    final AirbyteMessage logMessage = AirbyteMessageUtils.createLogMessage(AirbyteLogMessage.Level.WARN, "warning");

    final Stream<AirbyteMessage> messageStream = stringToMessageStream(Jsons.serialize(logMessage));

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).warn("warning");
    verifyNoMoreInteractions(logger);
  }

  @Test
  void testFailValidation() {
    final String invalidRecord = "{ \"fish\": \"tuna\"}";

    when(protocolPredicate.test(Jsons.deserialize(invalidRecord))).thenReturn(false);

    final Stream<AirbyteMessage> messageStream = stringToMessageStream(invalidRecord);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).error(anyString(), anyString());
    verifyNoMoreInteractions(logger);
  }

  @Test
  void testFailDeserialization() {
    final String invalidRecord = "{ \"type\": \"abc\"}";

    when(protocolPredicate.test(Jsons.deserialize(invalidRecord))).thenReturn(true);

    final Stream<AirbyteMessage> messageStream = stringToMessageStream(invalidRecord);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).error(anyString(), anyString());
    verifyNoMoreInteractions(logger);
  }

  @Test
  void testFailsSize() {
    final AirbyteMessage record1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green");

    final InputStream inputStream = new ByteArrayInputStream(record1.toString().getBytes(StandardCharsets.UTF_8));
    final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));

    final Stream<AirbyteMessage> messageStream =
        new DefaultAirbyteStreamFactory(protocolPredicate, logger, new Builder(), Optional.of(RuntimeException.class), 1l).create(bufferedReader);

    assertThrows(RuntimeException.class, () -> messageStream.toList());
  }

  @Test
  @Disabled
  void testMissingNewLineBetweenValidRecords() {
    final AirbyteMessage record1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "green");
    final AirbyteMessage record2 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow");

    final String inputString = Jsons.serialize(record1) + Jsons.serialize(record2);

    final Stream<AirbyteMessage> messageStream = stringToMessageStream(inputString);

    assertEquals(Collections.emptyList(), messageStream.collect(Collectors.toList()));
    verify(logger).error(anyString(), anyString());
    verifyNoMoreInteractions(logger);
  }

  private Stream<AirbyteMessage> stringToMessageStream(final String inputString) {
    final InputStream inputStream = new ByteArrayInputStream(inputString.getBytes(StandardCharsets.UTF_8));
    final BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));
    return new DefaultAirbyteStreamFactory(protocolPredicate, logger, new Builder(), Optional.empty()).create(bufferedReader);
  }

}
