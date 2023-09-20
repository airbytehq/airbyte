/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.mockito.Mockito.mockStatic;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.output.OutputRecordConsumerFactory;
import io.airbyte.integrations.base.output.PrintWriterOutputRecordConsumer;
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage.FailureType;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

public class AirbyteTraceMessageUtilityTest {

  private static MockedStatic<OutputRecordConsumerFactory> outputRecordConsumerFactory;

  private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();

  @BeforeAll
  public static void setup() {
    outputRecordConsumerFactory = mockStatic(OutputRecordConsumerFactory.class);
  }

  @BeforeEach
  public void setUpOut() {
    final PrintWriterOutputRecordConsumer printWriterOutputRecordConsumer = new PrintWriterOutputRecordConsumer(outContent);
    outputRecordConsumerFactory.when(OutputRecordConsumerFactory::getOutputRecordConsumer)
        .thenReturn(printWriterOutputRecordConsumer);
  }

  private void assertJsonNodeIsTraceMessage(JsonNode jsonNode) {
    // todo: this check could be better by actually trying to convert the JsonNode to an
    // AirbyteTraceMessage instance
    Assertions.assertEquals("TRACE", jsonNode.get("type").asText());
    Assertions.assertNotNull(jsonNode.get("trace"));
  }

  @Test
  void testEmitSystemErrorTrace() {
    AirbyteTraceMessageUtility.emitSystemErrorTrace(Mockito.mock(RuntimeException.class), "this is a system error");
    JsonNode outJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8));
    assertJsonNodeIsTraceMessage(outJson);
    Assertions.assertEquals("system_error", outJson.get("trace").get("error").get("failure_type").asText());
  }

  @Test
  void testEmitConfigErrorTrace() {
    AirbyteTraceMessageUtility.emitConfigErrorTrace(Mockito.mock(RuntimeException.class), "this is a config error");
    JsonNode outJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8));
    assertJsonNodeIsTraceMessage(outJson);
    Assertions.assertEquals("config_error", outJson.get("trace").get("error").get("failure_type").asText());
  }

  @Test
  void testEmitErrorTrace() {
    AirbyteTraceMessageUtility.emitErrorTrace(Mockito.mock(RuntimeException.class), "this is an error", FailureType.SYSTEM_ERROR);
    assertJsonNodeIsTraceMessage(Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8)));
  }

  @Test
  void testCorrectStacktraceFormat() {
    try {
      throw new RuntimeException();
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "you exploded the universe");
    }
    JsonNode outJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8));
    Assertions.assertTrue(outJson.get("trace").get("error").get("stack_trace").asText().contains("\n\tat"));
  }

}
