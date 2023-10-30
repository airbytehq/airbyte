/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Optional;
import lombok.SneakyThrows;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class AirbyteExceptionHandlerTest {

  PrintStream originalOut = System.out;
  private final ByteArrayOutputStream outContent = new ByteArrayOutputStream();
  private AirbyteExceptionHandler airbyteExceptionHandler;

  @BeforeEach
  public void setup() {
    System.setOut(new PrintStream(outContent, true, StandardCharsets.UTF_8));

    // mocking terminate() method in AirbyteExceptionHandler, so we don't kill the JVM
    airbyteExceptionHandler = spy(new AirbyteExceptionHandler());
    doNothing().when(airbyteExceptionHandler).terminate();
  }

  @Test
  void testTraceMessageEmission() throws Exception {
    runTestWithMessage("error");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    assertAll(
        () -> Assertions.assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.getTrace().getType()),
        () -> Assertions.assertEquals(AirbyteExceptionHandler.logMessage, traceMessage.getTrace().getError().getMessage()),
        () -> Assertions.assertEquals(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR, traceMessage.getTrace().getError().getFailureType())
    );
  }

  @Test
  void testMessageDeinterpolation() throws Exception {
    AirbyteExceptionHandler.STRINGS_TO_REMOVE.add("foo");
    AirbyteExceptionHandler.STRINGS_TO_REMOVE.add("bar");

    runTestWithMessage("Error happened in foo.bar");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    assertAll(
        () -> Assertions.assertEquals(AirbyteTraceMessage.Type.ERROR, traceMessage.getTrace().getType()),
        () -> Assertions.assertEquals("Error happened in foo.bar", traceMessage.getTrace().getError().getMessage()),
        () -> Assertions.assertEquals("Error happened in ?.?", traceMessage.getTrace().getError().getInternalMessage()),
        () -> Assertions.assertEquals(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR, traceMessage.getTrace().getError().getFailureType()),
        () -> Assertions.assertNull(traceMessage.getTrace().getError().getStackTrace(), "Stacktrace should be null if deinterpolating the error message")
    );
  }

  @Test
  void testMessageSmartDeinterpolation() throws Exception {
    AirbyteExceptionHandler.STRINGS_TO_REMOVE.add("foo");
    AirbyteExceptionHandler.STRINGS_TO_REMOVE.add("bar");

    runTestWithMessage("Error happened in foobar");

    final AirbyteMessage traceMessage = findFirstTraceMessage();
    Assertions.assertNotEquals("Error happened in ??", traceMessage.getTrace().getError().getMessage(), "foobar should not be deinterpolated");
  }

  private void runTestWithMessage(final String message) throws InterruptedException {
    // have to spawn a new thread to test the uncaught exception handling,
    // because junit catches any exceptions in main thread, i.e. they're not 'uncaught'
    final Thread thread = new Thread() {

      @SneakyThrows
      public void run() {
        final IntegrationRunner runner = Mockito.mock(IntegrationRunner.class);
        doThrow(new RuntimeException(message)).when(runner).run(new String[]{"write"});
        runner.run(new String[]{"write"});
      }

    };
    thread.setUncaughtExceptionHandler(airbyteExceptionHandler);
    thread.start();
    thread.join();
    System.out.flush();
  }

  @AfterEach
  public void teardown() {
    System.setOut(originalOut);
    AirbyteExceptionHandler.STRINGS_TO_REMOVE.clear();
  }
  private AirbyteMessage findFirstTraceMessage() {
    final Optional<AirbyteMessage> maybeTraceMessage = Arrays.stream(outContent.toString().split("\n"))
        .map(line -> Jsons.deserialize(line, AirbyteMessage.class))
        .filter(message -> message.getType() == AirbyteMessage.Type.TRACE)
        .findFirst();
    assertTrue(maybeTraceMessage.isPresent(), "Expected to find a trace message in stdout");
    return maybeTraceMessage.get();
  }
}
