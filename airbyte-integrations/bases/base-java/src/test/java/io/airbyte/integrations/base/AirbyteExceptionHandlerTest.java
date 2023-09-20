/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

import io.airbyte.integrations.base.output.OutputRecordConsumerFactory;
import io.airbyte.integrations.base.output.PrintWriterOutputRecordConsumer;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.slf4j.LoggerFactory;

public class AirbyteExceptionHandlerTest {

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

  @Test
  void testTraceMessageEmission() throws Exception {
    final AirbyteExceptionHandler airbyteExceptionHandler = spy(new AirbyteExceptionHandler());
    final Thread thread = new Thread();
    final Exception exception = new RuntimeException("error");

    doNothing().when(airbyteExceptionHandler).terminate();

    airbyteExceptionHandler.uncaughtException(thread, exception);

    // now we turn the std out from the thread into json and check it's the expected TRACE message
    JsonNode traceMsgJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8));
    LoggerFactory.getLogger(AirbyteExceptionHandlerTest.class).info(traceMsgJson.toString());
    Assertions.assertEquals("TRACE", traceMsgJson.get("type").asText());
    Assertions.assertEquals("ERROR", traceMsgJson.get("trace").get("type").asText());
    Assertions.assertEquals(AirbyteExceptionHandler.logMessage, traceMsgJson.get("trace").get("error").get("message").asText());
    Assertions.assertEquals("system_error", traceMsgJson.get("trace").get("error").get("failure_type").asText());
  }

}
