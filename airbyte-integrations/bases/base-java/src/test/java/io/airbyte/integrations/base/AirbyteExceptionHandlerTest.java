/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import lombok.SneakyThrows;
import org.junit.After;
import org.junit.Before;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.slf4j.LoggerFactory;

public class AirbyteExceptionHandlerTest {

  PrintStream originalOut = System.out;
  private volatile ByteArrayOutputStream outContent = new ByteArrayOutputStream();

  @Before
  public void setUpOut() {
    System.setOut(new PrintStream(outContent, true, StandardCharsets.UTF_8));
  }

  @Test
  void testTraceMessageEmission() throws Exception {
    // mocking terminate() method in AirbyteExceptionHandler, so we don't kill the JVM
    AirbyteExceptionHandler airbyteExceptionHandler = spy(new AirbyteExceptionHandler());
    doNothing().when(airbyteExceptionHandler).terminate();

    // have to spawn a new thread to test the uncaught exception handling,
    // because junit catches any exceptions in main thread, i.e. they're not 'uncaught'
    Thread thread = new Thread() {

      @SneakyThrows
      public void run() {
        setUpOut();
        final IntegrationRunner runner = Mockito.mock(IntegrationRunner.class);
        doThrow(new RuntimeException("error")).when(runner).run(new String[] {"write"});
        runner.run(new String[] {"write"});
      }

    };
    thread.setUncaughtExceptionHandler(airbyteExceptionHandler);
    thread.start();
    thread.join();
    System.out.flush();
    revertOut();

    // now we turn the std out from the thread into json and check it's the expected TRACE message
    JsonNode traceMsgJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8));
    LoggerFactory.getLogger(AirbyteExceptionHandlerTest.class).debug(traceMsgJson.toString());
    Assertions.assertEquals("TRACE", traceMsgJson.get("type").asText());
    Assertions.assertEquals("ERROR", traceMsgJson.get("trace").get("type").asText());
    Assertions.assertEquals(AirbyteExceptionHandler.logMessage, traceMsgJson.get("trace").get("error").get("message").asText());
    Assertions.assertEquals("system_error", traceMsgJson.get("trace").get("error").get("failure_type").asText());
  }

  @After
  public void revertOut() {
    System.setOut(originalOut);
  }

}
